from abc import abstractmethod

from pluma import Board
from pluma.test import TestBase


class DeviceActionBase(TestBase):
    __action_instance_id__ = 0

    def __init__(self, board: Board):
        super().__init__(board)
        DeviceActionBase.__action_instance_id__ += 1
        self._test_name += f'{DeviceActionBase.__action_instance_id__}'

    def test_body(self):
        self.execute()

    @abstractmethod
    def execute(self):
        pass

    @classmethod
    def parsing_error(cls, error: str):
        error_prefix = f'Invalid action for "{str(cls)}": '
        raise ValueError(error_prefix + error)
