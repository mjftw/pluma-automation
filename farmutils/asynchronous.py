from multiprocessing.pool import ThreadPool
import threading
import time


class AsyncSampler():
    '''Asynchronusly run a sample function in a separate thread at a given
        frequecy, to get a list of tuples of samples and times'''
    # Known issues:
    #   When exiting the main thread, while the sampler thread is running,
    #   the sampler thread does not terminate
    def __init__(self, sample_func):
        if not callable(sample_func):
            raise AttributeError('sample_func must be callable')
        self.sample_func = sample_func

        self._samples = []
        self._samples_lock = threading.Lock()
        self._sampling = threading.Event()
        self._sampling_thread = None

    def start(self, frequency, max_samples=None):
        if self._sampling.is_set():
            return False

        self._sampling_thread = threading.Thread(
            target=self._thread_method, args=(frequency, max_samples,))

        self._sampling.set()

        self._sampling_thread.start()

        return True

    def stop(self):
        if not self._sampling.is_set() or not self._sampling_thread:
            return None

        self._sampling.clear()

        self._sampling_thread.join()
        self._sampling_thread = None

        return self._samples

    def _thread_method(self, frequency, max_samples):
        self._samples_lock.acquire()
        self._samples = []
        self._samples_lock.release()

        while(self._sampling.is_set() and
                (max_samples is None or len(self._samples) < max_samples)):

            start_time = time.time()
            sample = (self.sample_func(), time.time())

            self._samples_lock.acquire()
            self._samples.append(sample)
            self._samples_lock.release()

            sleep_time = 1.0/frequency - (time.time()-start_time)
            if sleep_time > 0:
                time.sleep(sleep_time)


class Nonblocking:
    def __init__(self):
        self._thread_pool = ThreadPool(processes=1)
        self._thread_ident = threading.get_ident()

    class method:
        def __init__(self, fn):
            self.fn = fn
            self.async_result = None

            self.parent = None

        def get_return(self):
            if self.async_result:
                return self.async_result.get()

        def __get__(self, instance, owner):
            if instance is None:
                return self

            d = self
            # use a lambda to produce a bound method
            mfactory = lambda self, *args, **kw: d(self, *args, **kw)
            mfactory.__name__ = self.fn.__name__
            mfactory.get_return = self.get_return

            if not self.parent:
                # Make link to parent class
                self.parent = instance

            return mfactory.__get__(instance, owner)

        def __call__(self, *args, **kwargs):
            thread_ident = threading.get_ident()

            if thread_ident != self.parent._thread_ident:
                return self.fn(*args, **kwargs)

            def wrap_outer(fn):
                def wrap_inner(*args, **kwargs):
                    print('=== Starting worker thread === ')
                    retval = fn(*args, **kwargs)
                    print('=== Finished worker thread === ')

                    return retval
                return wrap_inner

            fn = wrap_outer(self.fn)

            self.async_result = self.parent._thread_pool.apply_async(
                func=fn, args=args, kwds=kwargs)

            return self
