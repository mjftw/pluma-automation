class TestSuite():
    def __init__(self, tests=None, setup_func=None, report_func=None,
            run_condition_func=None):
        self.tests = tests
        self.setup_args = None
        self.report_args = None
        self.run_condition_args = None
        self.setup_func = setup_func
        self.report_func = report_func
        self.run_condition_func = run_condition_func
        self.num_iterations_run = 0
        self.num_iterations_pass = 0
        self.num_iterations_fail = 0
        self.num_tests_run = 0
        self.num_tests_pass = 0
        self.num_tests_fail = 0

    def __call__(self):
        self.run()

    @property
    def tests(self):
        if hasattr(self, "_tests"):
            return self._tests
        else:
            return None

    @tests.setter
    def tests(self, tests):
        if isinstance(tests, list) and isinstance(tests[0], test):
            self._tests = tests
        elif isinstance(tests, test):
            self._tests = [tests]
        elif tests is None:
            self._tests = []
        else:
            raise AttributeError(
                "Must be either: single test, list of tests, or None")

    @property
    def setup_func(self):
        if hasattr(self, "_setup_func"):
            return self._setup_func
        else:
            return None

    @setup_func.setter
    def setup_func(self, f):
        """ Function with args """
        self.setup_args = [self]
        if isinstance(f, tuple) and callable(f[0]):
            self._setup_func = f[0]
            self.setup_args += list(f[1:])
        elif callable(f):
            self._setup_func = f
        elif f is None:
            self._setup_func = None
        else:
            raise AttributeError("Must be callable")

    @property
    def report_func(self):
        if hasattr(self, "_report_func"):
            return self._report_func
        else:
            return None

    @report_func.setter
    def report_func(self, f):
        self.report_args = [self]
        if isinstance(f, tuple) and callable(f[0]):
            self._report_func = f[0]
            self.report_args += list(f[1:])
        elif callable(f):
            self._report_func = f
        elif f is None:
            self._report_func = None
        else:
            raise AttributeError("Must be callable")

    @property
    def run_condition_func(self):
        if hasattr(self, "_run_condition_func"):
            return self._run_condition_func
        else:
            return None

    @run_condition_func.setter
    def run_condition_func(self, f):
        self.run_condition_args = [self]
        if isinstance(f, tuple) and callable(f[0]):
            self._run_condition_func = f[0]
            self.run_condition_args += list(f[1:])
        elif callable(f):
            self._run_condition_func = f
        elif f is None:
            self._run_condition_func = None
        else:
            raise AttributeError("Must be callable")

    def run_iteration(self):
        all_tests_pass = True
        for test in self.tests:
            success = test()
            self.num_tests_run += 1
            if success:
                self.num_tests_pass += 1
            else:
                self.num_tests_fail += 1
                all_tests_pass = False

        self.num_iterations_run += 1
        if all_tests_pass:
            self.num_iterations_pass += 1
        else:
            self.num_iterations_fail += 1

    def run(self):
        self.num_iterations_run = 0
        self.num_iterations_pass = 0
        self.num_iterations_fail = 0
        self.num_tests_run = 0
        self.num_tests_pass = 0
        self.num_tests_fail = 0

        if self.setup_func:
            print("Running suite setup function: {}".format(
                self.setup_func.__name__))
            self.setup_func(*self.setup_args)

        if self.run_condition_func:
            while self.run_condition_func(*self.run_condition_args):
                self.run_iteration()
        else:
            self.run_iteration()

        if self.report_func:
            print("Running suite report function: {}".format(
                self.report_func.__name__))
            self.report_func(*self.report_args)


class test():
    def __init__(self, fbody):
        self.args = None
        self.setup_args = None
        self.teardown_args = None
        self.fbody = fbody
        self.fsetup = None
        self.fteardown = None
        self.success = None

    def __call__(self, args=None):
        if args:
            if hasattr(args, '__ittr__'):
                self.args = list(args)
            else:
                self.args = args

        if self.fsetup:
            print("Running setup: {}".format(self.fsetup.__name__))
            if self.setup_args:
                self.fsetup(*self.setup_args)
            else:
                self.fsetup()

        if self.fbody:
            print("Starting test: {}".format(self.fbody.__name__))
            if self.args:
                self.success = self.fbody(*self.args)
            else:
                self.success = self.fbody()

        if self.fteardown:
            print("Running teardown: {}".format(self.fteardown.__name__))
            if self.teardown_args:
                self.fteardown(*self.teardown_args)
            else:
                self.fteardown()

        if isinstance(self.success, bool):
            return self.success

    def setup(self, fsetup):
        self.fsetup = fsetup
        return fsetup

    def teardown(self, fteardown):
        self.fteardown = fteardown
        return fteardown
