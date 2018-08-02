
import serial
import time

from farmcore.farm_base import FarmBase
from farmcore.usb import USB

# There are USB relays which have four channels 0,1,2,3
# The SDMUXes are connected to them
# The SDMUXes are also powered by the APC unit.


class USBRelay(FarmBase, USB):
    def __init__(self, usb_device):
        USB.__init__(self, usb_device)
        self.devnode = self.get_sdmux()
        self.log("Registered USBRelay at {}".format(self.devnode))

    @property
    def s(self):
        if self._s is None:
            self._s = serial.Serial(self.devnode, 9600)
        return self._s

    def write(self, data):
        return self.s.write(data)

    def __getitem__(self, key):
        return (self, key)

    def __repr__(self):
        return "USBRelay[{}]".format(self.usb_device)
