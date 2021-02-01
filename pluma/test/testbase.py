from abc import ABC, abstractmethod

from pluma.core import Board


class TestBase(ABC):
    """Base class for tests"""

    test_count = 0

    def __init__(self, board: Board = None, test_name: str = None):
        """Construct a TestBase with a board, and test suffix"""
        self.board = board

        if self.__class__.__module__:
            self._test_name = f'{self.__class__.__module__}.{self.__class__.__name__}'
        else:
            self._test_name = self.__class__.__name__

        TestBase.test_count += 1
        if test_name:
            self._test_name += f'[{test_name}]'
        self._test_name += f'#{TestBase.test_count}'

        # Settings to control this test instance
        self.settings = {}

        # Output data to be saved during the test
        self.data = {}

    def session_setup(self):
        '''Setup at the beginning of the test session'''

    def setup(self):
        '''Setup before the actual test runs'''

    @abstractmethod
    def test_body(self):
        '''Executed during the test'''

    def teardown(self):
        '''Cleanup after the test'''

    def session_teardown(self):
        '''Teardown at the end of the test session'''

    def save_data(self, data: dict = None, **data_kwargs: dict):
        '''Save some test data'''
        if data:
            self.data.update(data)
        if data_kwargs:
            self.data.update(data_kwargs)

    def __repr__(self):
        """Return a human-readable name for the test"""
        return self._test_name

    @classmethod
    def description(cls):
        return cls.__doc__


class NoopTest(TestBase):
    """An empty test which does nothing."""

    def test_body(self):
        pass
