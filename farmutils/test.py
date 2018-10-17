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

    def run(self):
        self.num_iterations_run = 0
        self.num_iterations_pass = 0
        self.num_iterations_fail = 0
        self.num_tests_run = 0
        self.num_tests_pass = 0
        self.num_tests_fail = 0

        if self.setup_func:
            args_string = ", ".join(str(e) for e in self.setup_args)
            print("Running suite setup function: {}({})".format(
                self.setup_func.__name__, args_string))
            self.setup_func(*self.setup_args)

        if self.run_condition_func:
            while self.run_condition_func(*self.run_condition_args):
                self.run_iteration()
        else:
            self.run_iteration()

        if self.report_func:
            args_string = ", ".join(str(e) for e in self.report_args)
            print("Running suite report function: {}({})".format(
                self.report_func.__name__, args_string))
            self.report_func(*self.report_args)


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
            if hasattr(args, '__ittr__'):
                self.args = list(args)
            else:
                self.args = args

        if self.fsetup:
            if self.setup_args:
                args_string = ", ".join(str(e) for e in self.setup_args)
                print("Running setup: {}({})".format(
                    self.fsetup.__name__, args_string))
                self.fsetup(*self.setup_args)
            else:
                print("Running setup: {}()".format(self.fsetup.__name__))
                self.fsetup()

        if self.fbody:
            if self.args:
                args_string = ", ".join(str(e) for e in self.args)
                print("Running test: {}({})".format(
                    self.fbody.__name__, args_string))
                self.success = self.fbody(*self.args)
            else:
                print("Running test: {}()".format(self.fbody.__name__))
                self.success = self.fbody()

        if self.fteardown:
            if self.teardown_args:
                args_string = ", ".join(str(e) for e in self.teardown_args)
                print("Running teardown: {}({})".format(
                    self.fteardown.__name__, args_string))
                self.fteardown(*self.teardown_args)
            else:
                print("Running teardown: {}()".format(self.fteardown.__name__))
                self.fteardown()

        if isinstance(self.success, bool):
            return self.success

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
