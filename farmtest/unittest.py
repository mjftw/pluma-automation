import time
from copy import copy


class TestFunctionNotSet(Exception):
    pass

""" Can be used as a function decorator """
class deferred_function():
    def __init__(self, f, *args, **kwargs):
        self.f = f

        self.name = None

        if args or kwargs:
            self.save_args(*args, **kwargs)
        else:
            self.args = None
            self.kwargs = None
            self.args_ready = True

    def __call__(self, *args, **kwargs):
            self.save_args(*args, **kwargs)
            return self

    def __repr__(self):
        args_str = '' if not self.args else ', '.join(
            [str(a) for a in self.args]
        )
        kwargs_str = '' if not self.kwargs else ', '.join(
            ["{}={}".format(k, v) for k, v in self.kwargs.items()]
        )
        return "{}({}{}{})".format(
            self.f.__name__, args_str, ', ' if args_str else '', kwargs_str)

    def __bool__(self):
        return self.args_ready

    def save_args(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.args_ready = True

    def run(self, suite=None):
        if self.args and self.kwargs:
            return self.f(suite, *self.args, **self.kwargs)
        elif self.args:
            return self.f(suite, *self.args)
        elif self.kwargs:
            return self.f(suite, **self.kwargs)
        else:
            return self.f(suite)


class UnitTestBase():
    def to_deffered_func(self, f, name=None):
        if f is None:
            return None

        new_f = None

        if isinstance(f, deferred_function):
            new_f = copy(f)
        else:
            if callable(f):
                new_f = deferred_function(f)
            else:
                raise AttributeError("Function must be callable")

        new_f.name = name
        return new_f


class UnitTestSuite(UnitTestBase):
    def __init__(self, tests=None, setup_func=None, report_func=None,
            run_condition_func=None, name=None, report_n_iterations=None,
            continue_on_fail=True, run_forever=False, iteration_end_sleep_s=0):
        self.tests = tests
        self.setup = setup_func
        self.report = report_func
        self.run_condition = run_condition_func

        self.name = name
        self.run_forever = run_forever
        self.report_n_iterations = report_n_iterations
        self.continue_on_fail = continue_on_fail
        self.iteration_end_sleep_s = iteration_end_sleep_s

        self.num_iterations_run = 0
        self.num_iterations_pass = 0
        self.num_iterations_fail = 0
        self.num_tests_run = 0
        self.num_tests_pass = 0
        self.num_tests_fail = 0

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
        self._setup = self.to_deffered_func(f, "setup")

    @property
    def report(self):
        return self._report

    @report.setter
    def report(self, f):
        self._report = self.to_deffered_func(f, "report")

    @property
    def run_condition(self):
        return self._run_condition

    @run_condition.setter
    def run_condition(self, f):
        self._run_condition = self.to_deffered_func(f, "run condition")

    def run_iteration(self):
        all_tests_pass = True
        for test in self.tests:
            success = test.run(self)
            self.num_tests_run += 1
            if success:
                self.num_tests_pass += 1
                if test not in self.tests_passed:
                    self.tests_passed.append(test)
            else:
                self.num_tests_fail += 1
                if test not in self.tests_failed:
                    self.tests_failed.append(test)
                all_tests_pass = False
            if not all_tests_pass and not self.continue_on_fail:
                break

        self.num_iterations_run += 1
        if all_tests_pass:
            self.num_iterations_pass += 1
        else:
            self.num_iterations_fail += 1

        if all_tests_pass or self.continue_on_fail:
            time.sleep(self.iteration_end_sleep_s)

        return all_tests_pass

    def run(self):
        self.num_iterations_run = 0
        self.num_iterations_pass = 0
        self.num_iterations_fail = 0
        self.num_tests_run = 0
        self.num_tests_pass = 0
        self.num_tests_fail = 0

        if self.setup:
            self.setup(self)

        while True:
            if self.run_condition:
                while self.run_condition.run(self):
                    success = self.run_iteration()
                    if not success and not self.continue_on_fail:
                        if self.report:
                            self.report.run(self)
                        return
                    if (self.report_n_iterations and
                        self.num_iterations_run % self.report_n_iterations == 0):
                        if self.report:
                            self.report.run(self)
            else:
                self.run_iteration()
                if self.report:
                    self.report.run(self)

            if not self.run_forever:
                return


class UnitTest(UnitTestBase):
    def __init__(self, fbody=None, fsetup=None, fteardown=None):
        self.success = False

        self.body = fbody
        self.setup = fsetup
        self.teardown = fteardown

    def __repr__(self):
        funcs = "{}:".format(__class__.__name__)
        if self.setup:
            funcs += "\n\t{}: {}".format(self.setup.name, str(self.setup))
        if self.body:
            funcs += "\n\t{}: {}".format(self.body.name, str(self.body))
        if self.teardown:
            funcs += "\n\t{}: {}".format(self.teardown.name, str(self.teardown))
        return funcs

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, f):
        self._body = self.to_deffered_func(f, "test")

    @property
    def setup(self):
        return self._setup

    @setup.setter
    def setup(self, f):
        self._setup = self.to_deffered_func(f, "setup")

    @property
    def teardown(self):
        return self._teardown

    @teardown.setter
    def teardown(self, f):
        self._teardown = self.to_deffered_func(f, "teardown")

    def run(self, suite=None):
        if not self.body:
            raise TestFunctionNotSet

        if self.setup:
            self.setup.run(suite)

        self.success = self.body.run(suite)

        if self.setup and self.teardown:
            self.teardown.run(suite)

        if self.success:
            return True
        else:
            return False
