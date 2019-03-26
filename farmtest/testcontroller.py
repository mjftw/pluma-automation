from .unittest import UnitTest, deferred_function


class TestController():
    def __init__(self, tests=None, setup_func=None, report_func=None,
            run_condition_func=None, name=None, report_n_iterations=None,
            continue_on_fail=True, run_forever=False, condition_check_interval_s=0,
            setup_every_iteration=False, force_initial_run=False, log_func=print):
        self.tests = tests
        self.setup = setup_func
        self.report = report_func
        self.run_condition = run_condition_func

        self.log_func = log_func or print

        self.name = name

        # Runtime settings
        self.settings = {}
        self.settings['run_forever'] = run_forever
        self.settings['report_n_iterations'] = report_n_iterations
        self.settings['continue_on_fail'] = continue_on_fail
        self.settings['condition_check_interval_s'] = condition_check_interval_s
        self.settings['setup_every_iteration'] = setup_every_iteration
        self.settings['force_initial_run'] = force_initial_run

        # Runtime statistics
        self.stats = {}
        self.stats['num_iterations_run'] = 0
        self.stats['num_iterations_pass'] = 0
        self.stats['num_iterations_fail'] = 0
        self.stats['num_tests_run'] = 0
        self.stats['num_tests_pass'] = 0
        self.stats['num_tests_fail'] = 0

        # Global data to be used by tests
        self.data = {}

        self.tests_passed = []
        self.tests_failed = []

    @property
    def tests(self):
        return self._tests

    @tests.setter
    def tests(self, tests):
        self._tests = []
        if isinstance(tests, list):
            for test in tests:
                if isinstance(test, UnitTest):
                    self._tests.append(test)
                elif callable(test):
                    self._tests.append(UnitTest(test))
                else:
                    raise AttributeError(
                        "Must be either: single test, list of tests, or None")
        elif isinstance(tests, UnitTest):
            self._tests = [tests]
        elif callable(tests):
            self._tests = [UnitTest(tests)]
        elif tests is None:
            self._tests = []
        else:
            raise AttributeError(
                "Must be either: single test, list of tests, or None")
        for test in self.tests:
            test.suite = self

    @property
    def setup(self):
        return self._setup

    @setup.setter
    def setup(self, f):
        self._setup = None if f is None else deferred_function(f)

    @property
    def report(self):
        return self._report

    @report.setter
    def report(self, f):
        self._report = None if f is None else deferred_function(f)

    @property
    def run_condition(self):
        return self._run_condition

    @run_condition.setter
    def run_condition(self, f):
        self._run_condition = None if f is None else deferred_function(f)

    def log(self, message):
        self.log_func('[{}] {}'.format(self.__class__.__name__, message))

    #FIXME: Currently the same test object is used for each test iterration,
    #   meaning that it maintains state. This causes many unexpected issues!
    #   This needs to be fixed so that each iteraction gets a clean test object.
    def run_iteration(self):
        self.log("Starting iteration: {}".format(
            self.stats['num_iterations_run']))
        if self.setup and self.settings['setup_every_iteration']:
            self.log("Running setup function: {}".format(self.setup))
            self.setup.run(self)

        all_tests_pass = True
        for test in self.tests:
            self.log("Running test: {}".format(test))
            success = test.run(self)
            self.stats['num_tests_run'] += 1
            if success:
                self.log("{} - PASS".format(test))
                self.stats['num_tests_pass'] += 1
                if test not in self.tests_passed:
                    self.tests_passed.append(test)
            else:
                self.log("{} - FAIL".format(test))
                self.stats['num_tests_fail'] += 1
                if test not in self.tests_failed:
                    self.tests_failed.append(test)
                all_tests_pass = False
            if not all_tests_pass and not self.settings['continue_on_fail']:
                break

        self.stats['num_iterations_run'] += 1
        if all_tests_pass:
            self.stats['num_iterations_pass'] += 1
            self.log("Test iteration complete: ALL TESTS PASSED")
        else:
            self.stats['num_iterations_fail'] += 1
            self.log("Test iteration complete: NOT ALL TESTS PASSED")

        return all_tests_pass

    #TODO: Add exception catching and email reporting
    def run(self):
        self.stats['num_iterations_run'] = 0
        self.stats['num_iterations_pass'] = 0
        self.stats['num_iterations_fail'] = 0
        self.stats['num_tests_run'] = 0
        self.stats['num_tests_pass'] = 0
        self.stats['num_tests_fail'] = 0

        self.log("Starting UnitTestSuite with settings: {}".format(
            self.settings))

        if self.setup and not self.settings['setup_every_iteration']:
            self.log("Running setup function: {}".format(self.setup))
            self.setup.run(self)

        while True:
            if self.run_condition:
                if (self.settings['force_initial_run'] and
                        self.stats['num_iterations_run'] == 0):
                    self.log("Ignoring run condition for first run")
                    run_now = True
                else:
                    self.log("Checking run condition function: {}".format(
                        self.run_condition))
                    run_now = self.run_condition.run(self)

                while run_now:
                    success = self.run_iteration()
                    if not success and not self.settings['continue_on_fail']:
                        if self.report:
                            self.log("Running report function: {}".format(self.report))
                            self.report.run(self)
                        return
                    if (self.settings['report_n_iterations'] and
                        self.stats['num_iterations_run'] % self.settings['report_n_iterations'] == 0):
                        if self.report:
                            self.log("Running report function: {}".format(self.report))
                            self.report.run(self)

                    self.log("Checking run condition function: {}".format(
                        self.run_condition))
                    run_now = self.run_condition.run(self)
            else:
                self.run_iteration()

            if self.report:
                self.log("Running report function: {}".format(self.report))
                self.report.run(self)

            if self.settings['run_forever']:
                if self.settings['condition_check_interval_s']:
                    self.log("Sleeping for {} seconds...".format(
                        self.settings['condition_check_interval_s']))
                    time.sleep(self.settings['condition_check_interval_s'])
            else:
                self.log("UnitTestSuite finished")
                return