
import serial
import time

from .farmclass import Farmclass
from .usb import USB
from .serialconsole import SerialConsole
from .relaybase import RelayBase

# There are USB relays which have four channels 0,1,2,3
# The SDMUXes are connected to them
# The SDMUXes are also powered by the APC unit.


class USBRelay(RelayBase, Farmclass, USB):
    port_map = [
        dict(a=b'1', b=b'q'),
        dict(a=b'2', b=b'w'),
        dict(a=b'3', b=b'e'),
        dict(a=b'4', b=b'r'),
    ]

    def __init__(self, hub):
        self.hub = hub
        self._console = None

        USB.__init__(self, None)

    @property
    def console(self):
        if self._console is None:
            self._console = SerialConsole(self.devnode, 9600)
        return self._console

    @property
    def devnode(self):
        return self.hub.get_relay()['devnode']

    @property
    def usb_device(self):
        return self.hub.get_relay()['usbpath']

    def unbind(self):
        self.console.close()
        USB.unbind(self)
        self._console = None

    def bind(self):
        USB.bind(self)
        self.console.open()

    def toggle(self, port, throw):
        if port not in range(1, 4):
            self.error("Port must be 1, 2, 3, or 4")
        if throw not in ['A', 'a', 'B', 'b']:
            self.error("Throw direction must be A or B")

        if throw in ['A', 'a']:
            self.console.send(self.port_map[port-1]['a'])

        if throw in ['B', 'b']:
            self.console.send(self.port_map[port-1]['b'])

    def __getitem__(self, key):
        return (self, key)

    def __repr__(self):
        return "USBRelay[{}]".format(self.usb_device)
