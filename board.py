#!/usr/bin/env python3

# import farm
# import hwconfig
#TODO: import Logging


class NoBoard(Exception):
    pass


class Board:
    def __init__(self, name, apc, hub, sdmux):
        self.apc = apc
        self.hub = hub
        self.sdmux = sdmux
        self.name = name
        # TODO: Add logging through Logger class

    def __repr__(self):
        return "\n[Board: name={}, {}, {}, {}]".format(
            self.name, self.apc, self.hub, self.sdmux
            )


def get_board(boards, name):
    for b in boards:
        if b.name == name:
            return b

    raise NoBoard("Can't find board with name[{}]".format(name))

# def get_board(name):
#     for b in boards:
#         if b.name == name:
#             return b

#     raise NoBoard("Can't find board called [{}]".format(name))


def get_name(boards, hub):
    for b in boards:
        if b.hub.usb == hub:
            return b.name

    return None


# def get(name, *a, **kw):
#     b = get_board(name)
#     print("{}".format(b))
#     return farm.farm(b, *a, **kw)
