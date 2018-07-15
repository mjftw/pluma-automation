
from farmclass import Farmclass
from usb import USB


class USBRelay(Farmclass, USB):
    def __init__(self, usbdev):
        USB.__init__(self, usbdev)

