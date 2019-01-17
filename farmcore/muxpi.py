import platform

from .farmclass import Farmclass
from .board import Board
from .serialconsole import SerialConsole
from .storagebase import StorageBase
from .powerbase import PowerBase
from .hub import Hub
from farmutils import run_host_cmd


class MuxPiError(Exception):
    pass


class MuxPi(Farmclass):
    required_version = 'MuxPi firmware v0.5'

    def __init__(self, dut_serial_mv, dut_serial_baud=115200, board=None):
        if platform.node() != 'nanopineo':
            raise MuxPiError('Not running on MuxPi!')

        self.dut_power = MuxPiPower(self)
        self.dut_storage = MuxPiStorage(self)
        self.internal_hub = Hub('2-1')

        self.stm_console = SerialConsole('/dev/ttyS2', 115200)
        self.dut_console = SerialConsole('/dev/ttyS1', dut_serial_baud)

        self.stm_cmd('echo off')
        version = self.stm_cmd('version')
        if version != self.required_version:
            raise MuxPiError('Incorrect MuxPi firmware version! Expected:[{}] Got:[{}]'.format(
                self.required_version, version))

        self.stm_cmd('uart {}'.format(dut_serial_mv))

        self.board = None
        if board:
            self.attach_board(board)

    def __repr__(self):
        return 'MuxPi'

    def attach_board(self, board):
        if not isinstance(board, Board):
            raise MuxPiError("Board given must be of the Board class")

        self.board = board

        self.board.power = self.dut_power
        self.board.storage = self.dut_storage
        self.board.console = self.dut_console
        self.board.hub = self.internal_hub

    def stm_cmd(self, cmd):
        '''
        Send command to the STM32.
        STM32 serial commands:
        help --- This help
        version --- Display version of the firmware
        echo --- Get (no arguments) or set ('on' or 'off') echo on serial "console": echo [on|off]. The default value is on.
        power --- Get (no arguments) or set ('on' or 'off') or switch off and on ('tick') power supply for DUT: power [on|off|tick]
        hdmi --- Get (no arguments) or set ('on' or 'off') HDMI HOTPLUG pin: hdmi [on|off]
        dyper --- Get (no second argument) or set ('on' or 'off') DyPer state: DYPER 1|2 [on|off]
        mux --- Connect microSD card to external connector (DUT) or card reader (TS): mux [DUT|TS]
        dut --- Connect microSD card and power to DUT: dut
        ts --- Connect microSD card and power to TS: ts
        led --- Get (no second or third argument) or set ('R G B') color of led (1 | 2), ex: led 1 255 0 255
        clr --- Clear the OLED display
        text --- Print text on the OLED display: text x y color content
        draw --- Draw an object on the OLED display: draw object x1 y1 [x2 y2], objects are:
                - point x y color - draws one point at given coordinates
                - line x1 y1 x2 y2 color - draws line between given coordinates
                - rectangle left top width height color - draws line between given coordinates
                - circle x y radius color - draws line between given coordinates
                color must be 'on', 'off' or 'inv'
        adc --- Print current adc value of all (if no arguments are given) or one specified channel, ex: adc 1
        voltage --- Print current voltage [mV] of all (if no arguments are given) or one specified channel, ex: voltage 1
        current --- Print current current [mA] being consumed by DUT
        lthor --- Get (no second argument) or set state of lthor control signals:
                - lthor switch [usb|uart] - redirect DUT's USB wires to NanoPi's 'usb' or 'uart'
                - lthor id [usb|uart] - switch DUT's USB to 'usb' or 'uart' mode
                - lthor vbus [on|off] - switch DUT's VBUS 'on' or 'off'
                - lthor combo [usb|uart] - make DUT and MuxPi USB work in 'usb' or 'uart' mode - no get function
        key --- Get current state of given key or both if no key number is given: key [1|2]
        uart --- Get current value of UART voltage or set if new value is given [in millivolts]
        '''
        recieved, __ = self.stm_console.send(cmd, match=['OK'],
            excepts=['Unknown command', 'Error processing command'])

        return recieved.strip() or None

    def stm_help(self):
        return self.stm_cmd('help')

class MuxPiPower(PowerBase):
    def __init__(self, muxpi):
        self.muxpi = muxpi
    
    def __repr__(self):
        return 'MuxPiPower'

    def on(self):
        self.muxpi.stm_cmd('power on')

    def off(self):
        self.muxpi.stm_cmd('power off')


class MuxPiStorage(StorageBase):
    def __init__(self, muxpi):
        self.muxpi = muxpi

    def __repr__(self):
        return 'MuxPiStorage'

    def to_host(self):
        self.muxpi.stm_cmd('mux TS')

    def to_board(self):
        self.muxpi.stm_cmd('mux DUT')