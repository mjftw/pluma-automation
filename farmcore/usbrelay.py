
import serial
import time

from .farmclass import Farmclass
from .usb import USB

# There are USB relays which have four channels 0,1,2,3
# The SDMUXes are connected to them
# The SDMUXes are also powered by the APC unit.


class USBRelay(Farmclass, USB):
    port_map = [
        dict(a=b'1', b=b'q'),
        dict(a=b'2', b=b'w'),
        dict(a=b'3', b=b'e'),
        dict(a=b'4', b=b'r'),
    ]

    def __init__(self, usb_device):
        USB.__init__(self, usb_device)
        self._devnode = None
        self._ser = None

    @property
    def devnode(self):
        if self._devnode is None:
            self._devnode = self.get_relay()
        return self._devnode

    @property
    def ser(self):
        if self._ser is None:
            self._ser = serial.Serial(self.devnode, 9600)
        return self._ser

    def write(self, data):
        return self.ser.write(data)

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
