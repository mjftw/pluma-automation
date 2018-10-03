#!/usr/bin/env python3

import sys
import serial

from .farmclass import Farmclass

class SDMux(Farmclass):
    """ SD Mux driver """
    def __init__(self, usbrelay, index, apc):
        self.usbrelay = usbrelay
        self.index = index
        self.apc = apc

    @property
    def serialdev(self):
        """ Check we can get tty device node every time we use it """
        return self.usbrelay.get_relay()

    def sdhost(self):
        """ Switch the SD card to the host """
        print("Switching SDMux on USB {}, index {} to host...".format(
            self.usbrelay.usbdev, self.index))
        self.usbrelay.rebind()
        self.usbrelay.toggle(self.index, 'A')

    def sdboard(self):
        """ Switch the SD card to the board """
        print("Switching SDMux on USB {}, index {} to board...".format(
            self.usbrelay.usb, self.index))
        self.usbrelay.rebind()
        self.usbrelay.toggle(self.index, 'B')
