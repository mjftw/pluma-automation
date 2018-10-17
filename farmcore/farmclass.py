from .hierachy import Hierachy
from .logging import Logging

class Farmclass(Hierachy, Logging):
    """ Contains functionality common to all farm objects """

    def __repr__(self):
        return self.show_hier(reccurse=False)
