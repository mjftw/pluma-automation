class TestSuite():
    def __init__(self, tests=None, setup_func=None, report_func=None):
        self.tests = tests
        self.setup_args = None
        self.report_args = None
        self.setup_func = setup_func
        self.report_func = report_func

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
        if isinstance(f, tuple) and callable(f[0]):
            self._setup_func = f[0]
            self.setup_args = list(f[1:])
        elif callable(f):
            self._setup_func = f
            self.setup_args = None
        elif f is None:
            self._setup_func = None
            self.setup_args = None
        else:
            raise AttributeError("Must be callable")

    @property
    def result_func(self):
        if hasattr(self, "_result_func"):
            return self._result_func
        else:
            return None

    @result_func.setter
    def result_func(self, f):
        if isinstance(f, tuple) and callable(f[0]):
            self._setup_func = f[0]
            self.setup_args = list(f[1:])
        elif callable(f):
            self._setup_func = f
            self.setup_args = None
        elif f is None:
            self._setup_func = None
            self.setup_args = None
        else:
            raise AttributeError("Must be callable")

    def run(self):
        if self.setup_func:
            if self.setup_args:
                self.setup_func(self.setup_args)
            else:
                self.setup_func()

        for test in self.tests:
            test()

        if self.report_func:
            if self.report_args:
                self.report_func(*self.report_args)
            else:
                self.report_func()


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
                self.fsetup(self.setup_args)
            else:
                self.fsetup()

        if self.fbody:
            print("Starting test: {}".format(self.fbody.__name__))
            if self.args:
                self.success = self.fbody(self.args)
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
