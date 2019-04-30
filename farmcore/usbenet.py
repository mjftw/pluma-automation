import os

from .usb import USB
from .interface import Interface
from .farmclass import Farmclass


class USBEnet(Farmclass, Interface, USB):
    device_path = '/sys/bus/usb/devices/'

    def __init__(self, usb_device):
        USB.__init__(self, usb_device)

    @property
    def interface(self):
        net_path = os.path.join(
            self.device_path, self.usb_device, 'net')
        iface_dirs = os.listdir(net_path)

        return None if not iface_dirs else iface_dirs[0]
