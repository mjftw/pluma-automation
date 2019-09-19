import threading
import time


def nonblocking(f):
    def wrap(*args, **kwargs):
        thread = threading.Thread(target=f, args=args, kwargs=kwargs)
        thread.start()

    return wrap


class Foo:
    def __init__(self):
        self.data = []
        self.last_data = None

    @nonblocking
    def slow_method(self):
        print("slow menthod started")

        for i in range(0, 10):
            self.data.append(i)
            self.save_last_data(i)
            time.sleep(1)

        print("slow menthod finished")

        # How to get return value out?
        return 'Hello world!'

    def save_last_data(self, i):
        self.last_data = self.data[-1]

