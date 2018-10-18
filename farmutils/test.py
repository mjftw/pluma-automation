""" Test func decorator  """
def test_func(f):
    def test(*args, **kwargs):
        return (f, args, kwargs)
    return test

class TestBase():
    def __call__(self):
        self.run()

    def __repr__(self):
        return self.__class__.__name__

    def create_func(self, f, name=""):
        if not f:
            return None

        func = {}

        if callable(f):
            try:
                if isinstance(f(), tuple) and len(f()) > 0 and callable(f()[0]):
                    f = f()
            except TypeError:
                f = test_func(f)()
        if isinstance(f, tuple) and callable(f[0]):
            func['f'] = f[0]
            func['args'] = list(filter(lambda x: isinstance(x, tuple), f[1:]))[0]
            func['kwargs'] = list(filter(lambda x: isinstance(x, dict), f[1:]))[0]
        else:
            raise AttributeError("Must be tuple of function, and (optional) args")

        if 'f' in func:
            func['name'] = name

        return func

    def run_func(self, func, echo=True):
        if not func:
            return None

        if 'f' in func:
            # args_string = ", ".join(str(e) for e in args)
            args_string = ", ".join(str(v) for v in func['args'])
            if func['kwargs']:
                args_string += ", " + ", ".join(
                    "{}={}".format(k, v) for k, v in func['kwargs'].items())
            if echo:
                print("Running {} function: {}({})".format(
                    func['name'], func['f'].__name__, args_string))

            return func['f'](self, *func['args'], **func['kwargs'])

    def attr_getter(self, attr):
        if hasattr(self, attr):
            return getattr(self, attr)
        else:
            return None

class TestSuite(TestBase):
    def __init__(self, tests=None, setup_func=None, report_func=None,
            run_condition_func=None, report_n_iterations=None, run_forever=False):
        self.tests = tests
        self.setup = setup_func
        self.report = report_func
        self.run_condition = run_condition_func
        self.run_forever = run_forever
        self.report_n_iterations = report_n_iterations

        self.num_iterations_run = 0
        self.num_iterations_pass = 0
        self.num_iterations_fail = 0
        self.num_tests_run = 0
        self.num_tests_pass = 0
        self.num_tests_fail = 0

    @property
    def tests(self):
        return self.attr_getter("_tests")

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
        for test in self.tests:
            test.suite = self

    @property
    def setup(self):
        return self.attr_getter("_setup")

    @setup.setter
    def setup(self, f):
        self._setup = self.create_func(f, "setup")

    @property
    def report(self):
        return self.attr_getter("_report")

    @report.setter
    def report(self, f):
        self._report = self.create_func(f, "report")

    @property
    def run_condition(self):
        return self.attr_getter("_run_condition")

    @run_condition.setter
    def run_condition(self, f):
        self._run_condition = self.create_func(f, "run_condition")

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
        while True:
            self.num_iterations_run = 0
            self.num_iterations_pass = 0
            self.num_iterations_fail = 0
            self.num_tests_run = 0
            self.num_tests_pass = 0
            self.num_tests_fail = 0

            self.run_func(self.setup)

            if self.run_condition:
                while self.run_func(self.run_condition, echo=False):
                    self.run_iteration()
                    if (self.report_n_iterations and
                        self.num_iterations_run % self.report_n_iterations == 0):
                        self.run_func(self.report)
            else:
                self.run_iteration()
                self.run_func(self.report)

            if not self.run_forever:
                return


class Test(TestBase):
    def __init__(self, fbody=None, fsetup=None, fteardown=None):
        self.body = fbody
        self.setup = fsetup
        self.teardown = fteardown

        self.suite = None
        self.success = False

    @property
    def body(self):
        return self.attr_getter("_body")

    @body.setter
    def body(self, f):
        self._body = self.create_func(f, "test")

    @property
    def setup(self):
        return self.attr_getter("_setup")

    @setup.setter
    def setup(self, f):
        self._setup = self.create_func(f, "setup")

    @property
    def teardown(self):
        return self.attr_getter("_teardown")

    @teardown.setter
    def teardown(self, f):
        self._teardown = self.create_func(f, "teardown")

    def run(self):
        self.run_func(self.setup)
        self.success = self.run_func(self.body)

        if self.setup:
            self.run_func(self.teardown)

        if self.success:
            return True
        else:
            return False
