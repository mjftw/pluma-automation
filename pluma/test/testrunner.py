from pluma.test.testgroup import GroupedTest
from pluma.core.board import Board
import traceback
import time
from abc import ABC, abstractmethod
from typing import Iterable, List, Union, cast

from pluma import utils
from pluma.core.baseclasses import LogLevel, Logger
from pluma.test import TestBase, TestGroup, AbortTesting

log = Logger()


class TestRunnerBase(ABC):
    '''Run a set of tests a single time and collect their settings and saved data'''

    def __init__(self, board: Board = None, tests: Union[TestBase, Iterable[TestBase]] = None,
                 email_on_fail: bool = None, continue_on_fail: bool = None):
        self.board = board
        self.email_on_fail = email_on_fail if email_on_fail is not None else False
        self.continue_on_fail = continue_on_fail if continue_on_fail is not None else False
        self.test_fails = []

        if isinstance(tests, TestBase):
            tests = [tests]
        elif tests is not None and isinstance(tests, Iterable):
            tests = list(tests)

        self._test_group = TestGroup(tests=tests)

        # General purpose data for use globally between tests
        self.data = {}

    @abstractmethod
    def _run(self, tests: Iterable[TestBase]) -> bool:
        '''Run the tests'''

    def run(self) -> bool:
        '''Run all tasks for all tests. Returns True if all succes and False otherwise'''
        log.log('Running tests')
        self.test_fails = []
        self.data = {}

        for test in self.tests:
            self._init_test_data(test_parent=self, test=test)

        try:
            # Defer the actual test running to classes that inherit this base
            return self._run(self.tests)
        except Exception as e:
            # Prevent exceptions from leaving test runner
            log.log('Testing aborted', color='red', bold=True, level=LogLevel.IMPORTANT)
            log.notice(f'  due to exception {e}', color='red')
            return False

    def __call__(self):
        return self.run()

    def __repr__(self):
        return f'[{self.__class__.__name__}]'

    def _init_test_data(self, test_parent, test: TestBase):
        '''Initialise the test data. Required for integration with TestController'''
        test.data = {}
        self.data[str(test)] = {
            'tasks': {
                'ran': [],
                'failed': {}
            },
            'data': test.data,
            'settings': test.settings,
            'order': test_parent.tests.index(test)
        }

        if isinstance(test, GroupedTest):
            for child_test in test.tests:
                self._init_test_data(test_parent=test, test=child_test)

    @property
    def tests(self) -> List[TestBase]:
        return self._test_group.tests

    @tests.setter
    def tests(self, tests: List[TestBase]):
        self._test_group.tests = tests

    def _run_task(self, test: TestBase, task_name: str) -> bool:
        '''Run a single task from a test'''
        task_func = getattr(test, task_name, None)
        if not task_func:
            log.error(f'Function {task_name} does not exist for test {test}')
            return False

        self.data[str(test)]['tasks']['ran'].append(task_name)

        try:
            task_func()
        # If exception is one we deliberately caused, don't handle it
        except KeyboardInterrupt as e:
            raise e
        except InterruptedError as e:
            raise e
        except Exception as e:
            self.data[str(test)]['tasks']['failed'][task_name] = str(e)

            # If request to abort testing, do so but don't run side effects and always reraise
            if isinstance(e, AbortTesting):
                log.error(f'Testing aborted in "{task_name}": {str(e)}')
                raise e

            log.debug(f'An exception occurred in "{task_name}": {str(e)}')

            self._handle_failed_task(test, task_name, e)
            return False

        return True

    def _handle_failed_task(self, test: TestBase, task_name: str, exception: Exception):
        '''Run any side effects for a task failure, such as writing logs or sending emails'''
        failed = {
            'time': time.time(),
            'test': test,
            'task': task_name,
            'exception': exception,
            'traceback': traceback.format_exc()
        }
        self.test_fails.append(failed)

        if self.email_on_fail:
            self.send_fail_email(exception, test, task_name)

        error = str(exception)
        if not error:
            error = exception.__class__.__name__

        log.error(f'Task failed: {error}', bold=True)
        log.debug(f'  details: {failed}')

    def send_fail_email(self, exception: Exception, test_failed: TestBase, task_failed: str):
        '''Send an email to the default email address explaining the test failure'''
        board_name = self.board.name if self.board else 'No Board'
        subject = (f'TestRunner Exception Occurred: [{str(test_failed)}: {task_failed}] '
                   f'[{board_name}]')
        body = f'''
        <b>Tests:</b> {[str(t) for t in self.tests]}<br>
        <b>Test Failed:</b> {str(test_failed)}<br>
        <b>Task Failed:</b> {task_failed}
        '''

        utils.send_exception_email(
            exception=exception,
            board=self.board,
            subject=subject,
            prepend_body=body
        )


class TestRunner(TestRunnerBase):
    '''Run a set of tests sequentially'''

    def _run(self, tests: Iterable[TestBase]) -> bool:
        success = True

        log.debug(f'Running tests: {list(map(str, self.tests))}')

        for test in tests:
            # Print test message
            test_message = str(test)
            column_limit = 70

            if len(test_message) > column_limit:
                test_message = f'{test_message[:column_limit-3]}...'

            is_group_test = isinstance(test, GroupedTest)
            log.log(test_message.ljust(column_limit) + '  ', level=LogLevel.IMPORTANT,
                    newline=is_group_test)

            log.hold()
            test_success = self._run_task(test, "setup")
            if test_success:
                test_success = self._run_task(test, "test_body")
                if test_success and is_group_test:
                    log.release()
                    test_success = self._run(cast(GroupedTest, test).tests)
                    log.hold()

                # Run teardown even if 'test_body' failed
                test_success &= self._run_task(test, "teardown")

            if is_group_test:
                log.log(test_message.ljust(column_limit) + '  ', level=LogLevel.IMPORTANT,
                        newline=False, bypass_hold=True)

            if test_success:
                log.log('PASS', color='green', level=LogLevel.IMPORTANT, bypass_hold=True)
            else:
                log.log('FAIL', color='red', level=LogLevel.IMPORTANT, bypass_hold=True)

            log.release()
            success &= test_success

            if not success and not self.continue_on_fail:
                raise AbortTesting('Aborting the execution (stop on failure)')

        return success
