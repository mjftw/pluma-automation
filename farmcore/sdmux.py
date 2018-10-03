
from .farm_base import FarmBase
import pyudev as pu

class SDMux(FarmBase):
    # Map is board/host
    sdmux_map = [
            dict(board=b'1', host=b'q'),
            dict(board=b'2', host=b'w'),
            dict(board=b'3', host=b'e'),
            dict(board=b'4', host=b'r'),
    ]

    def __init__(self, ur_port, apc_port):
        self.ur, self.ur_port = ur_port
        self.apc, self.apc_port = apc_port
        self._s = None

    # Write to the USB Relay device
    def host(self):
        self.ur.write(self.sdmux_map[self.ur_port]['host'])

    def board(self):
        self.ur.write(self.sdmux_map[self.ur_port]['board'])

    def on(self):
        self.apc.on(self.apc_port)

    def off(self):
        self.apc.off(self.apc_port)

    def __repr__(self):
        return "SDMUX {} {}".format(self.ur, self.apc)
