import os

from .usb import USB
from .interface import NetInterface
from .baseclasses import HardwareBase


class USBEnet(HardwareBase, NetInterface, USB):
    device_path = '/sys/bus/usb/devices/'

    def __init__(self, usb_device):
        USB.__init__(self, usb_device)

    @property
    def interface(self):
        net_path = os.path.join(
            self.device_path,
            self.usb_device,
            f'{self.usb_device}:1.0',
            'net')
        iface_dirs = os.listdir(net_path)

        return None if not iface_dirs else iface_dirs[0]
