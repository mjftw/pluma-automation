from .farmclass import Farmclass
from .storagebase import StorageBase


class SDMux(Farmclass, StorageBase):
    """ SD Mux driver """
    def __init__(self, usbrelay, index):
        self.usbrelay = usbrelay
        self.index = index

    @property
    def serialdev(self):
        """ Check we can get tty device node every time we use it """
        return self.usbrelay.get_relay()

    def to_host(self):
        print("Switching SDMux on USB {}, index {} to host...".format(
            self.usbrelay, self.index))
        self.usbrelay.toggle(self.index, 'A')

    def to_board(self):
        print("Switching SDMux on USB {}, index {} to board...".format(
            self.usbrelay, self.index))
        self.usbrelay.toggle(self.index, 'B')
