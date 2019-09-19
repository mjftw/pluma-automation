from multiprocessing.pool import ThreadPool
import time


class nonblocking:
    def __init__(self):
        self._thread_pool = ThreadPool(processes=1)

    class method:
        def __init__(self, fn):
            self.fn = fn
            self.async_result = None

            self.parent = None

        @property
        def retval(self):
            if self.async_result:
                return self.async_result.get()

        def __get__(self, instance, owner):
            if instance is None:
                return self

            d = self
            # use a lambda to produce a bound method
            mfactory = lambda self, *args, **kw: d(self, *args, **kw)
            mfactory.__name__ = self.fn.__name__
            mfactory.retval = self.retval

            # Make link to parent class
            self.parent = instance

            return mfactory.__get__(instance, owner)

        def __call__(self, *args, **kwargs):
            def wrap(*args, **kwargs):
                self.async_result = self.parent._thread_pool.apply_async(
                    func=self.fn, args=args, kwds=kwargs)

            return wrap(*args, **kwargs)


class Foo(nonblocking):
    def __init__(self):
        self.data = []
        self.last_data = None

        nonblocking.__init__(self)

    @nonblocking.method
    def slow_method(self, arg1):
        print("slow method started")

        for i in range(0, 10):
            self.data.append(i)
            self.save_last_data(i)
            time.sleep(1)

        print("slow method finished")

        return 'Hello world!'

    def save_last_data(self, i):
        self.last_data = self.data[-1]


f = Foo()
