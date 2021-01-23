from pluma.core import Board
from pluma.test import GroupedTest, TestList


class Session(GroupedTest):
    '''A group of tests organized as a session'''

    def __init__(self, board: Board = None, test_name: str = None,
                 tests: TestList = None):
        super().__init__(board=board, test_name=test_name, tests=tests)

    def setup(self):
        self.board.power.reboot()

    def teardown(self):
        self.board.power.off()
