from .farmclass import Farmclass


class RelayBase(Farmclass):
    def __init__(self):
        if type(self) is RelayBase:
            raise AttributeError(
                'This is a base class, and must be inherited')

    def toggle(f):
        def wrap(self, port, throw, *args, **kwargs):
            self.log('{}: Switching port {} to {}'.format(
                str(self), port, throw))
            f(self, port, throw, *args, **kwargs)
        return wrap
