from .hierachy import Hierachy
from .logging import Logging


class Farmclass(Hierachy, Logging):
    """ Contains functionality common to all farm objects """

    def __init__(self):
        if type(self) is Farmclass:
            raise AttributeError(
                'This is a base class, and must be inherited')

    def __repr__(self):
        return f'[{self.__class__.__name__}]'

    def __bool__(self):
        return True if type(self) is not Farmclass else False