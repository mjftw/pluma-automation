#!/usr/bin/env python3

# import farm
# import hwconfig

from farmclass import Farmclass
from interact import Interact
from serialconsole import SerialConsole

DEFAULT_LOGFILE = None

class NoBoard(Exception):
    pass


class Board(Farmclass):
    def __init__(self, name, apc, hub, sdmux, logfile=DEFAULT_LOGFILE):
        self.apc = apc
        self.hub = hub
        self.sdmux = sdmux
        self.name = name
        self.act = Interact()
        self.baud = 115200  # TODO: Remove hardcoding

        if logfile is DEFAULT_LOGFILE:
            self.logfile = "/tmp/board_{}_MWEBSTERDEV.log".format(self.name)
        else:
            self.logfile = logfile

        self.update_logger_hier()

    def update_logger_hier(self):
        """ Default logging format for boards """
        self.set_logger(
            logname=self.name,
            logfile=self.logfile,
            appendtype=True,
            logtime=True,
            reccurse=True
        )

    def init_console(self):
        if self.act.console is None:
            self.act.switch_console(
                SerialConsole(self.hub.get_tty(), self.baud))
            self.update_logger_hier()


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
