class Hub():
    def __init__(self, usb):
        self.usb = usb

    def __repr__(self):
        return "\n[Hub: usb={}]".format(self.usb)
