from .farmclass import Farmclass
from abc import ABCMeta, abstractmethod

class RelayBase(Farmclass, metaclass=ABCMeta):

    @abstractmethod
    def toggle(f):
        def wrap(self, port, throw, *args, **kwargs):
            self.log('{}: Switching port {} to {}'.format(
                str(self), port, throw))
            f(self, port, throw, *args, **kwargs)
        return wrap
