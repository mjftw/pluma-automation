import platform
import time
import threading

from .farmclass import Farmclass
from .board import Board
from .serialconsole import SerialConsole
from .storagebase import StorageBase
from .powerbase import PowerBase
from .relaybase import RelayBase
from .powerrelay import PowerRelay
from .hub import Hub


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

        self.sampling_current = False
        self.sampling_voltage = False

        self._current_samples = []
        self._sampling_current_stop = False
        self._sampling_current_thread = None
        self._voltage_samples = []
        self._sampling_voltage_stop = False
        self._sampling_voltage_thread = None

        self._stm_cmd_lock = False

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

    def sample_voltage(self):
        '''Returns the voltage on ADC2 in V. Max is 3.3V.
            ADC1 is connected to current sensor'''
        return float(
            self.stm_cmd('voltage 2').replace(' ', '').split(':')[1])/1000

    def sample_current(self):
        '''Returns the DUT current in mA'''
        return self.stm_cmd('current')

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
        while(self._stm_cmd_lock):
            pass

        self._stm_cmd_lock = True

        recieved, __ = self.stm_console.send(cmd, match=['OK'],
            excepts=['Unknown command', 'Error processing command'],
            log_verbose=False)

        self._stm_cmd_lock = False
        return recieved.strip() or None

    def stm_help(self):
        return self.stm_cmd('help')

    def start_sampling_current(self, frequency, max_samples=None):
        if self.sampling_current:
            return False

        self._sampling_current_thread = threading.Thread(
            target=self._current_thread_method, args=(frequency, max_samples,))

        self._sampling_current_thread.start()
        return True

    def stop_sampling_current(self):
        if not self.sampling_current or not self._sampling_current_thread:
            return None

        self._sampling_current_stop = True

        self._sampling_current_thread.join()
        self._sampling_current_thread = None

        return self._current_samples

    def _current_thread_method(self, frequency, max_samples):
        self._current_samples = []
        self.sampling_current = True

        while(not self._sampling_current_stop and
            (max_samples is None or
                len(self._current_samples) <= max_samples)):

            sample = (self.sample_current(), time.time())
            self._current_samples.append(sample)

            time.sleep(1.0/frequency)

        self.sampling_current = False
        self._sampling_current_stop = False

    def start_sampling_voltage(self, frequency, max_samples=None):
        if self.sampling_voltage:
            return False

        self._sampling_voltage_thread = threading.Thread(
            target=self._voltage_thread_method, args=(frequency, max_samples,))

        self._sampling_voltage_thread.start()
        return True

    def stop_sampling_voltage(self):
        if not self.sampling_voltage or not self._sampling_voltage_thread:
            return None

        self._sampling_voltage_stop = True

        self._sampling_voltage_thread.join()
        self._sampling_voltage_thread = None

        return self._voltage_samples

    def _voltage_thread_method(self, frequency, max_samples):
        self._voltage_samples = []
        self.sampling_voltage = True

        while(not self._sampling_voltage_stop and
            (max_samples is None or
                len(self._voltage_samples) <= max_samples)):

            sample = (self.sample_voltage(), time.time())
            self._voltage_samples.append(sample)

            time.sleep(1.0/frequency)

        self.sampling_voltage = False

class MuxPiPower(Farmclass, PowerBase):
    def __init__(self, muxpi):
        self.muxpi = muxpi

    def __repr__(self):
        return 'MuxPiPower'

    def on(self):
        self.muxpi.stm_cmd('power on')

    def off(self):
        self.muxpi.stm_cmd('power off')

    def reboot(self):
        self.off()
        time.sleep(0.25)
        self.on()

class MuxPiDyper(Farmclass, RelayBase):
    def __init__(self, muxpi):
        self.muxpi = muxpi

    def __repr__(self):
        return 'MuxPiDyper'

    def toggle(self, port, throw):
        if port not in [1, 2]:
            raise ValueError("Port must be 1 or 2. Given[{}]".format(
                port))
        if throw not in ['on', 'off']:
            raise ValueError("Throw direction must be 'on' or 'off'. Given[{}]".format(
                throw))

        self.muxpi.stm_cmd('dyper {} {}'.format(port, throw))

class MuxPiPowerDyper(Farmclass, PowerRelay):
    def __init__(self, muxpi, on_seq, off_seq):
        self.muxpi = muxpi
        PowerRelay.__init__(self, relay=MuxPiDyper(self.muxpi),
            on_seq=on_seq, off_seq=off_seq)

    def __repr__(self):
        return 'MuxPiPowerDyper'

    def reboot(self):
        self.off()
        self.on()


class MuxPiStorage(Farmclass, StorageBase):
    def __init__(self, muxpi):
        self.muxpi = muxpi

    def __repr__(self):
        return 'MuxPiStorage'

    def to_host(self):
        self.muxpi.stm_cmd('mux TS')

    def to_board(self):
        self.muxpi.stm_cmd('mux DUT')
