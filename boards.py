#!/usr/bin/env python3

import farm


class NoBoard(Exception):
    pass


# There are USB relays which have four channels 0,1,2,3
# The SDMUXes are connected to them
# The SDMUCes are also powered by the APC unit.

class USBRelay:
    def __init__(self, usb):
        self.usb = usb


class SDMux:
    def __init__(self, ur, index, apc):
        self.ur = ur
        self.index = index
        self.apc = apc


class Board:
    def __init__(self, name, apc, hub, sdmux):
        self.apc = apc
        self.hub = hub
        self.sdmux = sdmux
        self.name = name

    def __repr__(self):
        return "Farm Board [{}]".format(self.name)


ur1 = USBRelay(usb='1-1.1.4.1')
ur2 = USBRelay(usb='1-1.1.4.3')

sdm1 = SDMux(ur=ur2, index=0, apc=2)
sdm2 = SDMux(ur=ur2, index=3, apc=1)
sdm3 = SDMux(ur=ur2, index=2, apc=3)

sdms = [sdm1, sdm2, sdm3]

boards = [
        Board(name='bbb', apc=7, hub='1-1.1.1', sdmux=sdm1),
        Board(name='fb42', apc=4, hub='1-1.1.2', sdmux=sdm2),
        Board(name='fb43', apc=6, hub='1-1.1.3', sdmux=sdm3),
]


def get_board(name):
    for b in boards:
        if b.name == name:
            return b

    raise NoBoard("Can't find board called [{}]".format(name))


def get_name(hub):
    for b in boards:
        if b.hub == hub:
            return b.name

    return None


def get(name, *a, **kw):
    b = get_board(name)
    print("{}".format(b))
    return farm.farm(b, *a, **kw)
