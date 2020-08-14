import time

from farmcore import Board
from farmtest import TaskFailed
from farmcli import DeviceActionBase, DeviceActionRegistry


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
    def execute(self):
        self.board.power.off()
        time.sleep(1)
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
                                           'Wait duration must be a positive number, but got "{self.duration}" instead.')

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
