import inspect
from copy import copy


class TestFunctionNotSet(Exception):
    pass


class deferred_function():
    """ Can be used as a function decorator """
    def __init__(self, f, *args, **kwargs):
        if isinstance(f, deferred_function):
            self.f = copy(f.f)
            self.args = copy(f.args)
            self.kwargs = copy(f.kwargs)
        else:
            if not callable(f):
                raise AttributeError("Function must be callable")
            self.f = f
            self.args = args
            self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        return self

    def __repr__(self):
        args_str = '' if not self.args else ', '.join(
            [str(a) for a in self.args]
        )
        kwargs_str = '' if not self.kwargs else ', '.join(
            ["{}={}".format(k, v) for k, v in self.kwargs.items()]
        )

        if hasattr(self.f, '__name__'):
            name = self.f.__name__
        elif hasattr(self.f, '__class__') and hasattr(self.f.__class__, '__name__'):
            name = self.f.__class__.__name__
        else:
            name = self.__class__.__name__

        return "{}({}{}{})".format(
            name, args_str, ', ' if args_str and kwargs_str else '', kwargs_str)

    def run(self, TestController=None):
        # Check if first argument to function is 'TestController'
        expects_controller = next(iter(inspect.getargspec(self.f).args)) == 'TestController'

        args = self.args or []
        if expects_controller:
            args = [TestController] + list(args)

        if self.kwargs:
            return self.f(*args, **self.kwargs)
        else:
            return self.f(*args)


class UnitTest():
    def __init__(self, fbody=None, fsetup=None, fteardown=None, log_func=None):
        self.success = False

        self.body = fbody
        self.setup = fsetup
        self.teardown = fteardown

    def __repr__(self):
        funcs = "{}:".format(__class__.__name__)
        funcs += "\n\tSetup: {}".format(str(self.setup))
        funcs += "\n\tBody: {}".format(str(self.body))
        funcs += "\n\tTeardown: {}".format(str(self.teardown))
        return funcs

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, f):
        self._body = None if f is None else deferred_function(f)

    @property
    def setup(self):
        return self._setup

    @setup.setter
    def setup(self, f):
        self._setup = None if f is None else deferred_function(f)

    @property
    def teardown(self):
        return self._teardown

    @teardown.setter
    def teardown(self, f):
        self._teardown = None if f is None else deferred_function(f)

    def run(self, controller=None):
        if self.setup:
            self.setup.run(controller)

        if not self.body:
            raise TestFunctionNotSet

        self.success = self.body.run(controller)

        if self.setup and self.teardown:
            self.teardown.run(controller)

        if self.success:
            return True
        else:
            return False
