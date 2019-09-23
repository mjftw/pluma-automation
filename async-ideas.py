from multiprocessing.pool import ThreadPool
import time


class nonblocking:
    def __init__(self):
        self._thread_pool = ThreadPool(processes=1)
        self._running_async = False

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

            if not self.parent:
                # Make link to parent class
                self.parent = instance

            return mfactory.__get__(instance, owner)

        def __call__(self, *args, **kwargs):
            if self.parent._running_async:
                return self.fn(*args, **kwargs)

            def wrap_outer(fn):
                def wrap_inner(*args, **kwargs):
                    print('=== Entering worker thread ===')
                    self.parent._running_async = True

                    retval = fn(*args, **kwargs)

                    self.parent._running_async = False
                    print('=== Exiting worker thread ===')

                    return retval
                return wrap_inner

            fn = wrap_outer(self.fn)

            self.async_result = self.parent._thread_pool.apply_async(
                func=fn, args=args, kwds=kwargs)




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

        return 'Hello'

    @nonblocking.method
    def stacking_slow_method(self, *args, **kwargs):
        print("stacking_slow_method started")
        print(args, kwargs)

        time.sleep(1)
        retval = self.slow_method(None)

        print("stacking_slow_method finished")

        return f'{retval} World!'

    def save_last_data(self, i):
        self.last_data = self.data[-1]


f = Foo()
