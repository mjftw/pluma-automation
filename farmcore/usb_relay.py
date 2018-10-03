
import serial
import time
from farmcore.farm_base import FarmBase
from farmcore import usb

# There are USB relays which have four channels 0,1,2,3
# The SDMUXes are connected to them
# The SDMUCes are also powered by the APC unit.
class USBRelay(FarmBase):
    port_map = [
        dict(a=b'1', b=b'q'),
        dict(a=b'2', b=b'w'),
        dict(a=b'3', b=b'e'),
        dict(a=b'4', b=b'r'),
    ]
    def __init__(self, usbpath):
        self.usbpath = usbpath
        self.usb = usb.usb()
        self._s = None
        vendor = 'DLP_Design'
        if self.usbpath.startswith('/dev/ttyUSB'):
            self.devnode = self.usbpath
            self.usbpath = None
            return

        d = self.usb.get_device(self.usbpath)
        if d is None:
            return None
        for _ in range(20):
            for m in self.usb.puc.list_devices(subsystem='tty',  parent=d):
                if m.get('ID_VENDOR') is None:
                    continue
                if m['ID_VENDOR'] == vendor:
                    self.devnode = m.device_node
                    self.log("Registered USBRelay at {}".format(self.devnode))
                    return
            time.sleep(2)
        raise IOError('No usb-relay devices on '.format(usb_device))

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
