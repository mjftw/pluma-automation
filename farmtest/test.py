'''
class ExampleTest():
    def __init__(self, board):
        self.board = board

    # Any of the below tasks will be called at the correct time,
    # if they are implimented (All are optional)

    def __init__(self, board):
        self.board = board

    def prepare(self):
        pass

    def pre_board_on(self):
        pass

    def pre_board_mount(self):
        pass

    def pre_test_body(self):
        pass

    def test_body(self):
        pass

    def post_test_body(self):
        pass

    def post_board_off(self):
        pass

    def report(self):
        pass
'''

import sys
import traceback
import platform
import datetime
import time
import re
from copy import copy, deepcopy

from farmutils import Email, send_exception_email
from farmcore.exceptions import BoardBootValidationError, ConsoleLoginFailed


class TestingException(Exception):
    pass


class TaskFailed(TestingException):
    pass


class AbortTesting(TestingException):
    pass


class AbortTestingAndReport(AbortTesting):
    pass


class TestBase():
    #FIXME: These structs are shared between all instances of class!
    #  They shouldn't be.
    #  We're currently getting around this by having TestRunner set
    #  initilise the structs, but this is not ideal. FIX THIS.
    data = {}
    settings = {}

    def __init__(self, board, test_name_suffix=None):
        self.board = board
        self._test_name = self.__class__.__name__
        if test_name_suffix:
            assert isinstance(test_name_suffix, str)
            self._test_name += f'_{test_name_suffix}'

    def __repr__(self):
        return self._test_name

class BootTestBase(TestBase):
    boot_success = None

class TestCore(TestBase):
    tasks = [
        'pre_host_mount', '_host_mount', 'prepare', '_host_unmount',
        'pre_board_on', '_board_on_and_validate',
        'pre_board_login', '_board_login',
        'pre_board_mount', '_board_mount',
        'pre_test_body', 'test_body', 'post_test_body'
        '_board_unmount',
        '_board_off', 'post_board_off',
        '_host_mount', 'report'
    ]

    def pre_host_mount(self):
        self.board.log("\n=== PRE HOST MOUNT ===", colour='blue', bold=True)

    def _host_mount(self):
        self.board.log("\n=!= HOST MOUNT =!=", bold=True)
        self.board.storage.to_host()

        devnode = None
        for _ in range(1, 5):
            if not self.board.hub.get_part():
                time.sleep(1)
            else:
                devnode = self.board.hub.get_part('devnode')
                break
        if not devnode:
            raise TaskFailed('Cannot mount: No block device partition downstream of hub')

        self.board.storage.mount_host(devnode)

    def prepare(self):
        self.board.log("\n=== PREPARE ===", colour='blue', bold=True)

    def _host_unmount(self):
        self.board.log("\n=!= HOST UNMOUNT =!=", bold=True)

        #TODO: Move this functionality to the board class
        devnode = None
        for _ in range(1, 5):
            if not self.board.hub.get_part():
                time.sleep(1)
            else:
                devnode = self.board.hub.get_part('devnode')
                break
        if devnode:
            self.board.storage.unmount_host(devnode)
        else:
            self.board.log("Cannot find block device partition. Continuing anyway")

        self.board.storage.to_board()

    def pre_board_on(self):
        self.board.log("\n=== PRE BOARD ON ===", colour='blue', bold=True)

    def _board_on_and_validate(self):
        self.board.log("\n=!= BOARD ON AND VALIDATE =!=", bold=True)
        try:
            self.board.reboot_and_validate()
        except BoardBootValidationError as e:
            raise e

    def pre_board_login(self):
        self.board.log("\n=== PRE BOARD LOGIN ===", colour='blue', bold=True)

    def _board_login(self):
        self.board.log("\n=!= BOARD LOGIN =!=", bold=True)
        try:
            self.board.login()
        except ConsoleLoginFailed as e:
            raise TaskFailed(str(e))

    def pre_board_mount(self):
        self.board.log("\n=== PRE BOARD MOUNT ===", colour='blue', bold=True)

    def _board_mount(self):
        self.board.log("\n=!= BOARD MOUNT =!=", bold=True)
        self.board.storage.to_board()
        self.board.storage.mount_board()

    def pre_test_body(self):
        self.board.log("\n=== PRE TEST BODY ===", colour='blue', bold=True)

    def test_body(self):
        self.board.log("\n=== TEST BODY ===", colour='blue', bold=True)

    def post_test_body(self):
        self.board.log("\n=== POST TEST BODY ===", colour='blue', bold=True)

    def _board_unmount(self):
        self.board.log("\n=!= BOARD UNMOUNT =!=", bold=True)
        self.board.storage.unmount_board()

    def _board_off(self):
        self.board.log("\n=!= BOARD OFF =!=", bold=True)
        self.board.power.off()

    def post_board_off(self):
        self.board.log("\n=== POST BOARD OFF ===", colour='blue', bold=True)

    def report(self):
        self.board.log("\n=== REPORT ===", colour='blue', bold=True)


class TestRunner():
    def __init__(self, board, tests=None, boot_test=None,
            skip_tasks=None, email_on_fail=True, use_testcore=True,
            sequential=False):
        self.board = board
        self.email_on_fail = email_on_fail
        self.skip_tasks = skip_tasks or []
        self.tests = []
        if boot_test and not isinstance(boot_test, BootTestBase):
            raise AttributeError('Invalid boot test. Must inherit BootTestBase')
        self.boot_test = boot_test

        self.test_fails = []
        tests = tests or []
        if not isinstance(tests, list):
            tests = [tests]

        self.tasks = TestCore.tasks
        self.use_testcore = use_testcore
        self.sequential = sequential

        # General purpose data for use globally between tests
        self.data = {}

        if self.boot_test:
            self.add_test(self.boot_test)

        for test in tests:
            self.add_test(test)

    def __call__(self):
        return self.run()

    def __repr__(self):
        return f'[{self.__class__.__name__}]'

    @property
    def num_tests(self):
        return len(self.tests)

    def _init_test_data(self, test):
        test.settings = {}
        test.data = {}
        self.data[str(test)] = {
            'tasks': {
                'ran': [],
                'failed': []
            },
            'data': test.data,
            'settings': test.settings,
            'order': self.tests.index(test)
        }

    def run(self):
        self.test_fails = []

        # Init data
        self.data = {}

        # Add TestCore to run standard testing sequence of boots & mounts etc.
        if (self.use_testcore and "TestCore" not in
                (str(t) for t in self.tests)):
            self.add_test(TestCore(self.board), 0)

        # Init test data
        for test in self.tests:
            self._init_test_data(test)

        self.board.log("Running tests: {}".format(
            list(map(lambda t: str(t), self.tests))))

        if self.sequential:
            self.board.log('== TESTING MODE: SEQUENTIAL ==',
                colour='blue', bold=True)
            for test_name in (str(test) for test in self.tests
                    if str(test) != "TestCore"):
                for task_name in self.tasks:
                    # Run TestCore tasks for every test
                    tests_to_run = []
                    if self.use_testcore:
                        tests_to_run.append("TestCore")
                    tests_to_run.append(test_name)

                    self._run_tasks(task_name, tests_to_run)
        else:
            self.board.log('== TESTING MODE: PARALLEL ==',
                colour='blue', bold=True)
            self._run_tasks()

        self.board.log(f"\n== ALL TESTS COMPLETED ==",
            colour='blue', bold=True)

        # Check if any tasks failed
        if self.test_fails:
            return False
        else:
            return True

    def add_test(self, test, index=None):
        # Rename test if a test with the same name already added
        # Default name is the class name, new names are <classname>_1,2,3 etc.
        if not hasattr(test, '_test_name'):
            setattr(test, '_test_name', test.__class__.__name__)

        max_duplicate_tests = 500
        original_name = test._test_name
        stripped_name = re.sub(r'[0-9]+_', '', original_name[::-1], count=1)[::-1]

        for i in range(1, max_duplicate_tests+1):
            if not self._get_test_by_name(str(test._test_name)):
                break

            old_name = test._test_name
            test._test_name = f'{stripped_name}_{i}'

            self.board.log(
                'Test [{}] already added. Renaming to [{}]'.format(
                    old_name, test._test_name))

            if i >= max_duplicate_tests:
                raise TestingException(
                    'Maximum number [{}] of tests with name [{}] reached!'.format(
                        max_duplicate_tests, original_name))

        test = deepcopy(test)

        if index is None:
            self.board.log("Appending test: {}".format(str(test)))
            self.tests.append(test)
        else:
            self.board.log("Inserting test at position {}: {} ".format(
                index, str(test)))
            self.tests.insert(index, test)

    def rm_test(self, test):
        if test in self.tests:
            self.board.log("Removed test: {}".format(str(test)))
            self.tests.remove(test)

    def _get_test_by_name(self, test_name):
        tests = [t for t in self.tests if str(t) == test_name]
        if len(tests) > 1:
            raise TestingException('Found multiple tests with name {}'.format(
                test_name))

        return None if not tests else tests[0]

    def get_tests_with_task(self, task_name):
        tests = [t for t in self.tests if hasattr(t, task_name)]

        return None if not tests else tests

    def _run_tasks(self, task_names=None, test_names=None):
        # If task_names not specified, run all tasks
        if not task_names:
            task_names = self.tasks
        if not isinstance(task_names, list):
            task_names = [task_names]

        # If test_names not specified, run tasks for all tests
        if not test_names:
            test_names = [str(test) for test in self.tests]
        if not isinstance(test_names, list):
            test_names = [test_names]

        self.board.log(f'Running tasks {task_names} for tests {test_names}',
            colour='green', bold=True)

        try:
            for task_name in task_names:
                # Check if task should not be run
                skip_message = f'Skipping task: {task_name}'
                if "mount" in task_name and not self.board.storage:
                    self.board.log(skip_message + '. Board does not have storage',
                        colour='green', bold=True)
                    continue
                if task_name in self.skip_tasks:
                    self.board.log(skip_message, colour='green', bold=True)
                    continue

                for test_name in test_names:
                    self._run_task(task_name, test_name)
        except AbortTesting as e:
            self.board.log(f"\n== TESTING ABORTED EARLY ==",
                colour='red', bold=True)

    def _run_task(self, task_name, test_name):
        test = self._get_test_by_name(test_name)
        if not test:
            self.board.error(
                'Cannot run specified test {} as it is not in test list'.format(
                test_name, TestingException))

        if (task_name == "_board_on_and_validate" and
                self.boot_test):
            # Initialise boot test result to success
            self.boot_test.boot_success = True

        task_func = getattr(test, task_name, None)
        if not task_func:
            # If test does not have this task, then skip
            return

        self.data[str(test)]['tasks']['ran'].append(task_name)

        if test.__class__ == TestCore:
            # If only TestCore has task, and it is not an action
            #   (starts with '_'), do not run this task
            tests_with_task = [str(t) for t in self.get_tests_with_task(task_name)]
            if 'TestCore' in tests_with_task:
                tests_with_task.remove('TestCore')
            if not tests_with_task:
                return
        else:
            self.board.log("Running: {} - {}".format(
                str(test), task_name), colour='green')
        try:
            task_func()
        # If exception is one we deliberately caused, don't handle it
        except KeyboardInterrupt as e:
            raise e
        except InterruptedError as e:
            raise e
        except Exception as e:
            self.data[str(test)]['tasks']['failed'].append(task_name)

            # If request to abort testing, do so
            if isinstance(e, AbortTesting):
                self.board.log('Testing aborted by task {} - {}: {}'.format(
                    str(test), task_name, str(e)))
                if (isinstance(e, AbortTestingAndReport) and
                        'report' in self.tasks):
                    self._run_task('report')
                raise e
            # If failed boot, and we have a specific boot test,
            #   run it's report function
            if (isinstance(e, BoardBootValidationError) and
                    self.boot_test):
                    self.board.log('Boot test failed, running {}.report()'.format(
                        str(self.boot_test)))

                    self.boot_test.boot_success = False
                    self._run_task('report', str(self.boot_test))
                    self._handle_failed_task(test, task_name, e)
            # For all other exceptions, we want to know about it
            else:
                self._handle_failed_task(test, task_name, e)

    def _handle_failed_task(self, test, task_name, exception, abort=True):
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

        self.board.log('Task failed {}'.format(failed),
            colour='red', bold=True)

        if abort:
            raise AbortTesting(str(exception))

    def send_fail_email(self, exception, test_failed, task_failed):
        subject = 'TestRunner Exception Occured: [{}: {}] [{}]'.format(
            str(test_failed), task_failed, self.board.name)
        body = '''
        <b>Tests:</b> {}<br>
        <b>Test Failed:</b> {}<br>
        <b>Task Failed:</b> {}
        '''.format(
            [str(t) for t in self.tests],
            str(test_failed),
            task_failed)

        send_exception_email(
            exception=exception,
            board=self.board,
            subject=subject,
            prepend_body=body
        )