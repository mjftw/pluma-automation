#!/usr/bin/env python3

import sys
import serial

import usb

# Map is board/host
sdmux_map = [
        dict(board=b'1', host=b'q'),
        dict(board=b'2', host=b'w'),
        dict(board=b'3', host=b'e'),
        dict(board=b'4', host=b'r'),
]


class SDMux:
    """ SD Mux driver """
    def __init__(self, usbrelay, index, apc, baud=9600):
        self.usbrelay = usbrelay
        self.index = index
        self.apc = apc
        self.baud = baud

    def __repr__(self):
        return "\n[SDMux: {}, index={}, {} {}]".format(
            self.usbrelay, self.index, self.apc, self.usbrelay
        )

    def sdhost(self):
        """ Switch the SD card to the host """
        print("Switching SDMux on USB {}, index {} to host...".format(
            self.usbrelay.usb, self.index))
        usb.USB().rebind(self.usbrelay.usb)
        s = serial.Serial(self.serialdev, self.baud)
        s.write(sdmux_map[self.index]['host'])
        s.close()

    def sdboard(self):
        """ Switch the SD card to the board """
        print("Switching SDMux on USB {}, index {} to board...".format(
            self.usbrelay.usb, self.index))
        usb.USB().rebind(self.usbrelay.usb)
        s = serial.Serial(self.serialdev, self.baud)
        s.write(sdmux_map[self.index]['board'])
        s.close()
