#!/usr/bin/env python3

# import farm
# import hwconfig

from pexpect import TIMEOUT, EOF


from .farmclass import Farmclass
from .serialconsole import SerialConsole

DEFAULT_LOGFILE = object()

class NoBoard(Exception):
    pass

class BootValidationError(Exception):
    pass

class Board(Farmclass):
    def __init__(self, name, power, hub, sdmux,
                 console=None, bootstr=None, logfile=DEFAULT_LOGFILE):
        self.power = power
        self.hub = hub
        self.sdmux = sdmux
        self.name = name
        self.console = console or SerialConsole(hub.get_serial()['devnode'], 115200)
        self.bootstr = bootstr

        self.log_reccurse = True

        if logfile is DEFAULT_LOGFILE:
            self.log_file = "/tmp/board_{}.log".format(self.name)
        else:
            self.log_file = logfile

    def reboot_and_validate(self):
        if not self.bootstr:
            raise BootValidationError("Cannot validate boot. Not bootstring given")

        self.power.reboot()
        (__, matched) = self.console.send(match=self.bootstr, timeout=30)

        if matched is TIMEOUT or matched is EOF:
            raise BootValidationError("Did not get bootstring: {}".format(self.bootstr))


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
