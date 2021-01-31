from copy import copy
from typing import List, Optional

from pluma.test import TestBase
from pluma.core import Board
from pluma.core.baseclasses import Logger

TestList = List[TestBase]

log = Logger()


class TestGroup:
    '''A named set of tests'''

    def __init__(self, name: str = None, tests: List[TestBase] = None):
        self.name = name
        self._tests: List[TestBase] = []
        self.tests = tests if tests is not None else []

    def __str__(self):
        if self.name:
            return f'{self.__class__.__name__}[{self.name}]'
        else:
            return f'{self.__class__.__name__}'

    def __len__(self):
        return len(self.tests)

    @property
    def tests(self) -> List[TestBase]:
        return self._tests

    @tests.setter
    def tests(self, tests: List[TestBase]):
        if not isinstance(tests, list):
            raise TypeError(f'Expected a List[Testbase], but got {tests}')

        self._tests = []
        for test in tests:
            self.add_test(test)

    def add_test(self, test: TestBase):
        '''Add a test to the test list. Handles tests with same name by appending a number'''
        if not isinstance(test, TestBase):
            raise TypeError('The test must be a TestBase instance, '
                            f'but got {test} instead.')

        if self.get_test_by_name(str(test)) is not None:
            raise RuntimeError(f'Found duplicate test name {str(test)}!'
                               'This is a bug, please report it to the pluma '
                               'development team.')

        print(repr(test))
        test = copy(test)
        print("2: ", repr(test))

        log.debug(f'Added test "{test}" to group "{self}"')
        self._tests.append(test)

    def get_test_by_name(self, test_name: str) -> Optional[TestBase]:
        tests_with_name = [t for t in self.tests if str(t) == test_name]
        if len(tests_with_name) > 1:
            raise RuntimeError(f'Found multiple tests with name {test_name}, '
                               'this should not happen')

        return None if not tests_with_name else tests_with_name[0]


class GroupedTest(TestBase):
    '''A group of tests which can be handled as a test'''

    def __init__(self, board: Board = None, test_name: str = None,
                 tests: TestList = None):
        super().__init__(board=board, test_name=test_name)

        self.test_group = TestGroup(tests=tests)

    @property
    def tests(self) -> TestList:
        return self.test_group.tests

    def test_body(self):
        for test in self.tests:
            test.setup()
            test.test_body()
            test.teardown()
