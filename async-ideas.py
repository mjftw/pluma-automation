from multiprocessing.pool import ThreadPool
from threading import Thread
import time


class nonblocking:
    def __init__(self, fn):
        self.fn = fn
        self.pool = ThreadPool(processes=1)
        self.async_result = None

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

        return mfactory.__get__(instance, owner)

    def __call__(self, *args, **kwargs):
        def wrap(*args, **kwargs):
            self.async_result = self.pool.apply_async(
                func=self.fn, args=args, kwds=kwargs)

        return wrap(*args, **kwargs)


class Foo:
    def __init__(self):
        self.data = []
        self.last_data = None

    @nonblocking
    def slow_method(self, arg1):
        print("slow method started")

        for i in range(0, 10):
            self.data.append(i)
            self.save_last_data(i)
            time.sleep(1)

        print("slow method finished")

        # How to get return value out?
        return 'Hello world!'

    def save_last_data(self, i):
        self.last_data = self.data[-1]

f = Foo()