#!/usr/bin/env python3

# import farm
# import hwconfig

from farmclass import Farmclass


class NoBoard(Exception):
    pass


class Board(Farmclass):
    def __init__(self, name, apc, hub, sdmux, baud=115200):
        self.apc = apc
        self.hub = hub
        self.sdmux = sdmux
        self.name = name
        self.baud = baud
        self.console = None

    def get_console(self):
        if self.console is None:
            self.console = Console(hub.get_tty(), self.baud)


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
