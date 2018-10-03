from board import Board
from usb import USB
from usbrelay import USBRelay
from sdmux import SDMux
from apc import APC
from apc import get_apc
from hub import Hub

# There are USB relays which have four channels 0,1,2,3
# The SDMUXes are connected to them
# The SDMUCes are also powered by the APC unit.

usbrelays = [
    USBRelay(usbdev='1-1.1.4.1'),
    USBRelay(usbdev='1-1.1.4.3'),
]

hubs = [
    Hub(usbdev='1-1.1.1'),
    Hub(usbdev='1-1.1.2'),
    Hub(usbdev='1-1.1.3'),
]

apcs = [
    APC(host='apc1', user='apc', pw='apc', port=1),
    APC(host='apc1', user='apc', pw='apc', port=2),
    APC(host='apc1', user='apc', pw='apc', port=3),
    APC(host='apc1', user='apc', pw='apc', port=4),
    APC(host='apc1', user='apc', pw='apc', port=5),
    APC(host='apc1', user='apc', pw='apc', port=6),
    APC(host='apc1', user='apc', pw='apc', port=7),
    APC(host='apc1', user='apc', pw='apc', port=8),
]

sdmuxs = [
    SDMux(
        usbrelay=usbrelays[1],
        index=0,
        apc=get_apc(apcs, 'apc1', 2),
    ),
    SDMux(
        usbrelay=usbrelays[1],
        index=3,
        apc=get_apc(apcs, 'apc1', 1),
    ),
    SDMux(
        usbrelay=usbrelays[1],
        index=2,
        apc=get_apc(apcs, 'apc1', 3),
    ),
]

boards = [
    Board(
        name='bbb',
        apc=get_apc(apcs, 'apc1', 7),
        hub=hubs[0],
        sdmux=sdmuxs[0]
    ),
    Board(
        name='fb42',
        apc=get_apc(apcs, 'apc1', 4),
        hub=hubs[1],
        sdmux=sdmuxs[1]
    ),
    Board(
        name='fb43',
        apc=get_apc(apcs, 'apc1', 6),
        hub=hubs[2],
        sdmux=sdmuxs[2]
    ),
]
