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
import shutil
import os
import inspect
from copy import copy

from farmutils import Email, send_exception_email, datetime_to_timestamp
from farmcore.exceptions import BoardBootValidationError, ConsoleLoginFailedError


class TestingException(Exception):
    pass


class TaskFailed(TestingException):
    pass


class AbortTesting(TestingException):
    pass


class AbortTestingAndReport(AbortTesting):
    pass


class TestBase():
    def __init__(self, board, test_name_suffix=None):
        self.board = board
        self._test_name = self.__class__.__name__
        if test_name_suffix:
            assert isinstance(test_name_suffix, str)
            self._test_name += f'_{test_name_suffix}'

        # Settings to control this test instance
        self.settings = {}

        # Output data to be saved during the test
        self.data = {}

    def __repr__(self):
        return self._test_name


class TestCore(TestBase):
    tasks = [
        '_init_test_state',
        'pre_host_mount', '_host_mount', 'prepare', '_host_unmount',
        'pre_board_on', '_board_on_and_validate',
        'pre_board_login', '_board_login',
        'pre_board_mount', '_board_mount',
        'pre_test_body', 'test_body', 'post_test_body'
        '_board_unmount',
        '_board_off', 'post_board_off',
        '_host_mount', 'report'
    ]

    def __init__(self, board, failed_bootlogs_dir):
        TestBase.__init__(self, board)

        self.failed_bootlogs_dir = failed_bootlogs_dir

    def _init_test_state(self):
        self.board.log("\n=!= INIT TEST STATE =!=", bold=True)

        self.settings['failed_bootlogs_dir'] = self.failed_bootlogs_dir

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
            boot_time = self.board.reboot_and_validate()
        except BoardBootValidationError as e:
            # If boot failed, save this info and backup logfile
            self.data['boot_success'] = False
            self.data['boot_log'] = os.path.join(
                self.settings['failed_bootlogs_dir'],
                '{}_failed_boot_{}.log'.format(self.board.name,
                    datetime_to_timestamp(datetime.datetime.now())))

            try:
                if not os.path.exists(self.settings['failed_bootlogs_dir']):
                    os.makedirs(self.settings['failed_bootlogs_dir'])
                shutil.copy2(self.board.console.log_file, self.data['boot_log'])
            except Exception as ex:
                self.data['boot_log'] = None
                raise ex

            self.board.error('Boot failed! Saving console log to {}'.format(
                self.data['boot_log']))
            raise e

        # If boot succeeded save this info
        self.data['boot_success'] = True
        self.data['boot_time'] = boot_time

    def pre_board_login(self):
        self.board.log("\n=== PRE BOARD LOGIN ===", colour='blue', bold=True)

    def _board_login(self):
        self.board.log("\n=!= BOARD LOGIN =!=", bold=True)
        try:
            self.board.login()
        except ConsoleLoginFailedError as e:
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
    def __init__(self, board, tests=None,
            skip_tasks=None, email_on_fail=True, use_testcore=True,
            sequential=False, failed_bootlogs_dir=None,
            continue_on_fail=False):
        self.board = board
        self.email_on_fail = email_on_fail
        self.continue_on_fail = continue_on_fail
        self.failed_bootlogs_dir = failed_bootlogs_dir or '/tmp/lab'
        self.skip_tasks = skip_tasks or []
        self.test_fails = []

        if not isinstance(tests, list):
            tests = [tests]
        self.tests = tests

        self.tasks = TestCore.tasks
        self.use_testcore = use_testcore
        self.sequential = sequential

        # General purpose data for use globally between tests
        self.data = {}

        # Validate 'skip_tasks'
        for task_to_skip in self.skip_tasks:
            if task_to_skip not in self.tasks:
                raise ValueError(
                    f'The tasks "{task_to_skip}" in the tasks to skip is not a valid task.\nValid tasks are: {self.tasks}')

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
            self.add_test(TestCore(self.board, self.failed_bootlogs_dir), 0)

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
        # Check if user accidentally passed in a class inheriting
        # TestBase, instead of an instance of that class.
        if inspect.isclass(test) and (test is TestBase or issubclass(test, TestBase)):
            raise AttributeError(
                'test passed in is TestBase class or a subclass of it.  '
                'It should be an object instance of either TestBase or '
                'a subclass.  Possible cause: tests list passed to TestRunner'
                ' contains <testClassName> instead of <testClassName>().'
            )
        # Verify that test is an instance of class TestBase.
        if not isinstance(test, TestBase):
            raise AttributeError(
                'test should be an object instance of class TestBase'
                ' or one of its subclasses.'
            )

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

        test = copy(test)

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


        try:
            for task_name in task_names:
                tests_with_task = self.get_tests_with_task(task_name)

                # If no tests have this task, do not attempt to run it
                if not tests_with_task:
                    continue

                tests_names_with_task = [str(t) for t in tests_with_task]

                # If only TestCore has task, and it is not an action
                #   (starts with '_'), do not run this task
                if ('TestCore' in tests_names_with_task and
                        not task_name.startswith('_')):
                    tests_names_with_task.remove('TestCore')
                if not tests_names_with_task:
                    continue

                # Check if task should not be run
                skip_message = f'Skipping task: {task_name}'
                if "mount" in task_name and not self.board.storage:
                    self.board.log(skip_message + '. Board does not have storage',
                        colour='green', bold=True)
                    continue
                if (( task_name in ['_board_on_and_validate', '_board_off'])
                        and not self.board.power):
                    self.board.log(skip_message + '. Board does '
                        'not have power control', colour='green', bold=True)
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

        task_func = getattr(test, task_name, None)
        if not task_func:
            # If test does not have this task, then skip
            return

        self.data[str(test)]['tasks']['ran'].append(task_name)

        if test.__class__ != TestCore:
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

            abort_testing = not self.continue_on_fail
            self._handle_failed_task(test, task_name, e, abort_testing)

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