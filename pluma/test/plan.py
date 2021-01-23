from pluma.core import Board
from pluma.test import GroupedTest, TestList


class Plan(GroupedTest):
    '''A group of tests organized as a plan.

    A test plan is the highest level way of grouping tests.
    '''

    def __init__(self, board: Board = None, test_name: str = None,
                 tests: TestList = None):
        super().__init__(board=board, test_name=test_name, tests=tests)
