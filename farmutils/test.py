from . import testlib

class TestSuite():
    def __init__(self, tests=None, setup_func=None, report_func=None,
            run_condition_func=None, report_n_iterations=None, run_forever=False):
        self.tests = tests
        self.setup_args = None
        self.report_args = None
        self.run_condition_args = None
        self.setup_func = setup_func
        self.report_func = report_func
        self.run_condition_func = run_condition_func
        self.run_forever = run_forever
        self.report_n_iterations = report_n_iterations
        self.num_iterations_run = 0
        self.num_iterations_pass = 0
        self.num_iterations_fail = 0
        self.num_tests_run = 0
        self.num_tests_pass = 0
        self.num_tests_fail = 0

    def __call__(self):
        self.run()

    def __repr__(self):
        return self.__class__.__name__

    @property
    def tests(self):
        if hasattr(self, "_tests"):
            return self._tests
        else:
            return None

    @tests.setter
    def tests(self, tests):
        if isinstance(tests, list) and isinstance(tests[0], Test):
            self._tests = tests
        elif isinstance(tests, Test):
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

    def run_func(self, f, args, name=""):
        if f:
            args_string = ", ".join(str(e) for e in args)
            print("Running suite {} function: {}({})".format(
                name, f.__name__, args_string))
            return f(*args)

    def run_setup(self):
        return self.run_func(self.setup_func, self.setup_args, "setup")

    def run_report(self):
        return self.run_func(self.report_func, self.report_args, "report")

    def run(self):
        while True:
            self.num_iterations_run = 0
            self.num_iterations_pass = 0
            self.num_iterations_fail = 0
            self.num_tests_run = 0
            self.num_tests_pass = 0
            self.num_tests_fail = 0

            self.run_setup()

            if self.run_condition_func:
                while self.run_condition_func(*self.run_condition_args):
                    self.run_iteration()
                    if (self.report_n_iterations and
                        self.num_iterations_run % self.report_n_iterations == 0):
                        self.run_report()
            else:
                self.run_iteration()

            self.run_report()

            if not self.run_forever:
                return


class Test():
    def __init__(self, fbody=None, fsetup=None, fteardown=None):
        self.args = None
        self.setup_args = None
        self.teardown_args = None
        self.fbody = fbody
        self.fsetup = fsetup
        self.fteardown = fteardown
        self.success = None

    def __call__(self, args=None):
        if args:
            if isinstance(args, list):
                self.args = args
            else:
                self.args = [args]

        self.run_setup()

        self.success = self.run_body()

        self.run_teardown()

        if isinstance(self.success, bool):
            return self.success

    def run_func(self, f, name, args=None):
        result = None
        if f:
            if args:
                args_string = ", ".join(str(e) for e in args)
                print("Running {}: {}({})".format(
                    name, f.__name__, args_string))
                result = f(*args)
            else:
                print("Running teardown: {}()".format(f.__name__))
                result = f()

        return result

    def run_setup(self):
        return self.run_func(self.fsetup, "setup", self.setup_args)

    def run_body(self):
        return self.run_func(self.fbody, "test", self.args)

    def run_teardown(self):
        return self.run_func(self.fteardown, "teardown", self.teardown_args)

    def setup(self, f):
        self.fsetup = f
        return f

    def teardown(self, f):
        self.fteardown = f
        return f

    @property
    def fsetup(self):
        return self._fsetup

    @fsetup.setter
    def fsetup(self, f):
        if isinstance(f, tuple) and callable(f[0]):
            self._fsetup = f[0]
            self.setup_args = list(f[1:])
        elif callable(f):
            self._fsetup = f
            self.setup_args = None
        elif f is None:
            self._fsetup = None
            self.setup_args = None
        else:
            raise AttributeError("Must be callable")

    @property
    def fteardown(self):
        return self._fteardown

    @fteardown.setter
    def fteardown(self, f):
        if isinstance(f, tuple) and callable(f[0]):
            self._fteardown = f[0]
            self.teardown_args = list(f[1:])
        elif callable(f):
            self._fteardown = f
            self.teardown_args = None
        elif f is None:
            self._fteardown = None
            self.teardown_args = None
        else:
            raise AttributeError("Must be callable")
