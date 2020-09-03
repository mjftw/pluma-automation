from threading import Lock


class Locking:
    global_lock = Lock()

    class method:
        '''
        Decorates class methods in order to make them lockling.
        '''

        def __init__(self, fn):
            self.fn = fn

            self.parent = None

        def __get__(self, instance, owner):
            if instance is None:
                return self

            d = self
            # use a lambda to produce a bound method
            mfactory = lambda self, *args, **kw: d(self, *args, **kw)
            mfactory.__name__ = self.fn.__name__

            if not self.parent:
                # Make link to parent class
                self.parent = instance

            return mfactory.__get__(instance, owner)

        def __call__(self, *args, **kwargs):
            '''
            Intercept function calls and wait to get class global lock before calling.
            '''

            self.parent.__class__.global_lock.acquire()
            result = self.fn(*args, **kwargs)
            self.parent.__class__.global_lock.release()

            return result
