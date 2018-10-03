
import serial
import time

from farmcore.farm_base import FarmBase
from farmcore.usb import USB

# There are USB relays which have four channels 0,1,2,3
# The SDMUXes are connected to them
# The SDMUXes are also powered by the APC unit.


class USBRelay(FarmBase, USB):
    sdmux_map = [
        dict(a=b'1', b=b'q'),
        dict(a=b'2', b=b'w'),
        dict(a=b'3', b=b'e'),
        dict(a=b'4', b=b'r'),
    ]
    def __init__(self, usb_device):
        USB.__init__(self, usb_device)
        self.devnode = self.get_relay()
        self.log("Registered USBRelay at {}".format(self.devnode))

    @property
    def s(self):
        if self._s is None:
            self._s = serial.Serial(self.devnode, 9600)
        return self._s

    def write(self, data):
        return self.s.write(data)

    def toggle(self, port, throw):
        if port not in range(1, 4):
            self.err("Port must be 1, 2, 3, or 4")
        if throw not in ['A', 'a', 'B', 'b']:
            self.err("Throw direction must be A or B")

        if throw in ['A', 'a']:
            self.write(self.port_map[port-1]['a'])

        if throw in ['B', 'b']:
            self.write(self.port_map[port-1]['b'])

    def __getitem__(self, key):
        return (self, key)

    def __repr__(self):
        return "USBRelay[{}]".format(self.usbpath)
