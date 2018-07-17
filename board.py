#!/usr/bin/env python3

# import farm
# import hwconfig

from farmclass import Farmclass
from console import Console


class NoBoard(Exception):
    pass


class Board(Farmclass):
    def __init__(self, name, apc, hub, sdmux):
        self.apc = apc
        self.hub = hub
        self.sdmux = sdmux
        self.name = name
        self.console = None

#TODO: Get hub to give the tty_device node
    def init_console(self, tty_dev, baud=115200):
        if self.console is None:
            self.console = Console(tty_dev, baud)


def get_board(boards, name):
    for b in boards:
        if b.name == name:
            return b

    raise NoBoard("Can't find board with name[{}]".format(name))


def get_name(boards, hub):
    for b in boards:
        if b.hub.usb == hub.usb:
            return b.name

    return None


# def get(name, *a, **kw):
#     b = get_board(name)
#     print("{}".format(b))
#     return farm.farm(b, *a, **kw)
