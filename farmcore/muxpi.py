import platform

from .farmclass import Farmclass
from farmutils.helpers import run_host_cmd
from .storagebase import StorageBase


class MuxPiError(Exception):
    pass


class MuxPi(Farmclass):
    def __init__(self, board=None):
        if 'nanopineo' not in platform.machine():
            raise MuxPiError('Not running on MuxPi!')

        self._board = None

        self.dut_power = MuxPiPower(self)
        self.dut_storage = MuxPiStorage(self)
        self.board = board

    @property
    def board(self):
        return self._board

    @board.setter
    def board(self, board):
        self._board = board
        self._board.power = self.dut_power
        # self._board.hub = self.internal_hub
        self._board.storage = self.dut_storage


    def stm_cmd(self, cmd):
        cmd = 'stm -{}'.format(cmd)
        (output, rc) = run_host_cmd(cmd)
        if rc != 0:
            raise MuxPiError(
                "Error sending command to stm32! cmd={}, output={}".format(
                cmd, output))

class MuxPiPower():
    def __init__(self, muxpi):
        self.muxpi = muxpi

    def on(self):
        raise NotImplementedError()

    def off(self):
        raise NotImplementedError()

    def reboot(self):
        self.muxpi.stm_cmd('tick')

class MuxPiStorage(StorageBase):
    def __init__(self, muxpi):
        self.muxpi = muxpi

    #TODO:  Impliment functions
