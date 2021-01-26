from abc import abstractmethod

from pluma import Board
from pluma.test import TestBase


class DeviceActionBase(TestBase):
    def test_body(self):
        self.execute()

    @abstractmethod
    def execute(self):
        pass

    @classmethod
    def parsing_error(cls, error: str):
        error_prefix = f'Invalid action for "{str(cls)}": '
        raise ValueError(error_prefix + error)
