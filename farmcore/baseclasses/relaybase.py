from .farmclass import Farmclass
from abc import ABCMeta, abstractmethod

class RelayBase(Farmclass, metaclass=ABCMeta):
    def __init__(self):
        super(RelayBase, self).__init__()
        if type(self) is RelayBase:
            raise AttributeError(
                'This is a base class, and must be inherited')

    @abstractmethod
    def toggle(f):
        def wrap(self, port, throw, *args, **kwargs):
            self.log('{}: Switching port {} to {}'.format(
                str(self), port, throw))
            f(self, port, throw, *args, **kwargs)
        return wrap
