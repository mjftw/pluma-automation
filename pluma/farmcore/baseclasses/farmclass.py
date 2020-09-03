from .hierarchy import Hierarchy
from .logging import Logging


class Farmclass(Hierarchy, Logging):
    """ Contains functionality common to all farm objects """

    def __repr__(self):
        return f'[{self.__class__.__name__}]'
