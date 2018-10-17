#!/usr/bin/env python3

# import farm
# import hwconfig

from .farmclass import Farmclass
from .serialconsole import SerialConsole

DEFAULT_LOGFILE = object()

class NoBoard(Exception):
    pass


class Board(Farmclass):
    def __init__(self, name, power, hub, sdmux, logfile=DEFAULT_LOGFILE):
        self.power = power
        self.hub = hub
        self.sdmux = sdmux
        self.name = name
        self.baud = 115200  # TODO: Remove hardcoding
        self._console = None

        self.log_reccurse = True

        if logfile is DEFAULT_LOGFILE:
            self.log_file = "/tmp/board_{}.log".format(self.name)
        else:
            self.log_file = logfile

    @property
    def console(self):
        if self._console is None:
            self._console = SerialConsole(self.hub.get_serial(), self.baud)
        return self._console


def get_board(boards, name):
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


def show_info(board):
    u = usb.USB(board.hub)

    print("\n =============== Device [{} - {}] =============".format(
        u.usb_device, get_name(u.usb_device)))

    blockinfo = u.filter_downstream({
        'subsystem': 'block',
        'devtype': 'disk'
    }, {
        'size': 0
    })
    for info in blockinfo:
        print("Block device: {}, {:4.2f}MB".format(
            info['devnode'], (info['size']/(1024 * 1024))))

    serialinfo = u.filter_downstream({
        'subsystem': 'tty'
    })
    for info in serialinfo:
        print(("Serial device: {}, {}".format(
            info['devnode'], info['vendor'])))

    up = usb.USB(u.get_parent())
    pinfo = up.devinfo
    if pinfo:
        print("Parent is: {} , {}".format(
            pinfo['sysname'], pinfo['devtype']))
