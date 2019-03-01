import threading
import time

# Known issues:
#   When exiting the main thread, while the sampler thread is running,
#   the sampler thread does not terminate


class AsyncSampler():
    '''Asynchronusly run a sample function in a separate thread at a given
        frequecy, to get a list of tuples of samples and times'''
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
                (max_samples is None or len(self._samples) <= max_samples)):

            sample = (self.sample_func(), time.time())
            self._samples_lock.acquire()
            self._samples.append(sample)
            self._samples_lock.release()

            time.sleep(1.0/frequency)
