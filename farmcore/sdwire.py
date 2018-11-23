from pyftdi.ftdi import Ftdi

from .farmclass import Farmclass
from .storagebase import StorageBase


class SDWire(Farmclass, StorageBase):
    def __init__(self, serial=None):
        self.serial = serial
        self.ftdi = Ftdi()

        self.vendor_id = 0x04e8
        self.product_id = 0x6001

    def _open(self):
        self.ftdi.open(
            vendor=self.vendor_id,
            product=self.product_id,
            serial=self.serial
        )

    def _close(self):
        self.ftdi.close()

    def to_host(self):
        self._open()
        self.ftdi.set_bitmode(mode=0x20, bitmask=0xf1)
        self._close()

    def to_board(self):
        self._open()
        self.ftdi.set_bitmode(mode=0x20, bitmask=0xf0)
        self._close()