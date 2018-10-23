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
            func['str'] = "{}({})".format(
                func['f'].__name__,
                ", ".join([str(a) for a in func['args']] + [
                "{}={}".format(k, v) for k, v in func['kwargs'].items()]))
        else:
            raise AttributeError("Must be tuple of function, and (optional) args")

        if 'f' in func:
            func['name'] = name

        return func

    def run_func(self, func, echo=True):
        if not func:
            return None

        if 'f' in func:
            if echo:
                print("Running {} function: {}".format(
                    func['name'], func['str']))

            if hasattr(self, "suite") and self.suite:
                suite = self.suite
            else:
                suite = None

            return func['f'](suite, *func['args'], **func['kwargs'])

    def attr_getter(self, attr):
        if hasattr(self, attr):
            return getattr(self, attr)
        else:
            return None

class TestSuite(TestBase):
    def __init__(self, tests=None, setup_func=None, report_func=None,
            run_condition_func=None, name=None, report_n_iterations=None,
            continue_on_fail=True, run_forever=False):
        self.tests = tests
        self.setup = setup_func
        self.report = report_func
        self.run_condition = run_condition_func

        self.name = name
        self.run_forever = run_forever
        self.report_n_iterations = report_n_iterations
        self.continue_on_fail = continue_on_fail

        self.suite = self

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
        return self.attr_getter("_tests")

    @tests.setter
    def tests(self, tests):
        self._tests = []
        if isinstance(tests, list):
            for test in tests:
                if isinstance(test, Test):
                    self._tests += test
                elif callable(test):
                    self._tests += Test(test)
                else:
                    raise AttributeError(
                        "Must be either: single test, list of tests, or None")
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
        print("In report setter")
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
            success = test.run()
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
            return True
        else:
            self.num_iterations_fail += 1
            return False

    def run(self):
        self.num_iterations_run = 0
        self.num_iterations_pass = 0
        self.num_iterations_fail = 0
        self.num_tests_run = 0
        self.num_tests_pass = 0
        self.num_tests_fail = 0

        self.run_func(self.setup)

        while True:
            if self.run_condition:
                while self.run_func(self.run_condition, echo=False):
                    success = self.run_iteration()
                    if not success and not self.continue_on_fail:
                        self.run_func(self.report)
                        return
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

    def __repr__(self):
        funcs = "{}:".format(__class__.__name__)
        if self.setup:
            funcs += "\n\t{}: {}".format(self.setup['name'], self.setup['str'])
        if self.body:
            funcs += "\n\t{}: {}".format(self.body['name'], self.body['str'])
        if self.teardown:
            funcs += "\n\t{}: {}".format(self.teardown['name'], self.teardown['str'])
        return funcs

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
