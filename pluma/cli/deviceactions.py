import os
import sys
import time

from pluma.core.baseclasses import Logger, LogLevel
from pluma import Board
from pluma.test import TaskFailed
from pluma.cli import DeviceActionBase, DeviceActionRegistry

log = Logger()


@DeviceActionRegistry.register()
class PowerOnAction(DeviceActionBase):
    def execute(self):
        self.board.power.on()


@DeviceActionRegistry.register()
class PowerOffAction(DeviceActionBase):
    def execute(self):
        self.board.power.off()


@DeviceActionRegistry.register()
class PowerCycleAction(DeviceActionBase):
    def __init__(self, board: Board, off_duration_ms: float = None):
        super().__init__(board)
        self.off_duration_ms = off_duration_ms or 1000

    def execute(self):
        self.board.power.off()
        time.sleep(self.off_duration_ms / 1000)
        self.board.power.on()


@DeviceActionRegistry.register()
class LoginAction(DeviceActionBase):
    def execute(self):
        self.board.login()


@DeviceActionRegistry.register()
class WaitAction(DeviceActionBase):
    def __init__(self, board: Board, duration: int):
        super().__init__(board)
        self.duration = duration

        if self.duration < 0:
            DeviceActionBase.parsing_error(self.__class__,
                                           'Wait duration must be a positive number, '
                                           'but got "{self.duration}" instead.')

    def validate(self):
        return self.duration >= 0

    def execute(self):
        time.sleep(self.duration)


@DeviceActionRegistry.register()
class WaitForPatternAction(DeviceActionBase):
    def __init__(self, board: Board, pattern: str, timeout: int = None):
        super().__init__(board)
        self.pattern = pattern
        self.timeout = timeout if timeout else 15

    def execute(self):
        self.board.console.read_all()
        matched_output = self.board.console.wait_for_match(match=self.pattern,
                                                           timeout=self.timeout)
        if not matched_output:
            raise TaskFailed(
                f'{str(self)}: Timeout reached while waiting for pattern "{self.pattern}"')


@DeviceActionRegistry.register()
class SetAction(DeviceActionBase):
    def __init__(self, board: Board, device_console: str = None):
        super().__init__(board)

        self.device_console = device_console

        if self.device_console and not self.board.get_console(self.device_console):
            raise ValueError(f'Cannot set console to "{self.device_console}": '
                             'no such console was set for this board')

    def execute(self):
        if self.device_console:
            log.log(f'Setting device console to {self.device_console}')
            self.board.console = self.board.get_console(self.device_console)


@DeviceActionRegistry.register()
class CopyToDeviceAction(DeviceActionBase):
    def __init__(self, board: Board, file: str, destination: str, timeout: int = 15):
        super().__init__(board)
        self.file = file
        self.destination = destination
        self.timeout = timeout

    def execute(self):
        log.log(f'Copying {self.file} to target device destination {self.destination}')
        self.board.console.copy_to_target(self.file, self.destination, self.timeout)


@DeviceActionRegistry.register('manual_action')
class ManualDeviceAction(DeviceActionBase):
    '''Print a message, and wait for the user to press ENTER'''

    def __init__(self, board: Board, message: str, name: str = None):
        super().__init__(board)
        if name:
            self._test_name += f'[{name}]'
        self.message = message

        if not sys.__stdin__.isatty():
            raise ValueError('Non-interactive shell detected: '
                             'Manual actions must be used in an interactive shell')

    def execute(self):
        log.log(f'{os.linesep}Manual action:'
                f'{os.linesep}  > {self.message}'
                f'{os.linesep}Press ENTER when done',
                level=LogLevel.INFO, bypass_hold=True, newline=False)
        input()
