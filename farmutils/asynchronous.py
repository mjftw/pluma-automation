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
    '''
    This is a base class that allows the inheriting class to mark
    its methods as nonblocking, by decorating them with @Nonblocking.method.
    If a method marked as nonblocking is called, it is run in a separate
    thread, and the calling thread continues execution while the method runs.
    In order to get the return value of this method, the client can call the
    <instance>.<method_name>.await_return() class method. This will cause the
    client thread to block until the nonblocking method has finished, at which
    point the return value is read.
    If a method marked as nonblocking calls another nonblocking method (from
    its worker thread), a new worker thread will not be spawned, and the
    function call will happen in the usual blocking manner in the worker
    thread. This is to prevent an unbounded number of thread from being
    created.
    Optionally multiple worker threads can be created, but the default
    number of worker threads is one per Nonblocking class.
    If the client calls a nonblocking method while all (usually only one) the
    worker threads are in use, then the nonblocking method call will be added
    to a queue, and called once a worker thread is free.
    '''
    def __init__(self, threads=1):
        '''
        Use @threads to specify number of worker threads. You probably
        want to leave this at the default of 1 to prevent concurrency issues.
        '''
        self._thread_pool = ThreadPool(processes=threads)
        self._thread_ident = threading.get_ident()

    class method:
        def __init__(self, fn):
            self.fn = fn
            self.async_result = None

            self.parent = None

        def await_return(self):
            if self.async_result:
                return self.async_result.get()

        def __get__(self, instance, owner):
            if instance is None:
                return self

            d = self
            # use a lambda to produce a bound method
            mfactory = lambda self, *args, **kw: d(self, *args, **kw)
            mfactory.__name__ = self.fn.__name__
            mfactory.await_return = self.await_return

            if not self.parent:
                # Make link to parent class
                self.parent = instance

            return mfactory.__get__(instance, owner)

        def __call__(self, *args, **kwargs):
            thread_ident = threading.get_ident()

            if thread_ident != self.parent._thread_ident:
                return self.fn(*args, **kwargs)

            self.async_result = self.parent._thread_pool.apply_async(
                func=self.fn, args=args, kwds=kwargs)

            return self
