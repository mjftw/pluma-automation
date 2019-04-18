from .hierachy import Hierachy
from .logging import Logging


class Farmclass(Hierachy, Logging):
    """ Contains functionality common to all farm objects """

    def __repr__(self):
        return self.show_hier(reccurse=False)

    def __bool__(self):
        return True if type(self) is not Farmclass else False