import usb


class USBRelay:
    def __init__(self, usb):
        self.usb = usb

    def __repr__(self):
        return "\n[USBRelay: {}]".format(self.usb)
