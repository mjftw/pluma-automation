import sys
import traceback
import platform
import datetime

from farmutils.doemail import Email

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

    def post_board_mount(self):
        pass

    def test_body(self):
        pass

    def pre_board_unmount(self):
        pass

    def post_board_off(self):
        pass

    def report(self):
        pass
'''

import time

from farmcore.console import LoginFailed
from farmcore.board import BootValidationError


class TaskFailed(Exception):
    pass


class TestBase():
    tasks_failed = []


class TestCore(TestBase):
    tasks = [
        '_host_mount', 'prepare', '_host_unmount',
        'pre_board_on', '_board_on_and_validate',
        'pre_board_login', '_board_login',
        'pre_board_mount', '_board_mount', 'post_board_mount',
        'test_body',
        'pre_board_unmount', '_board_unmount',
        '_board_off', 'post_board_off',
        '_host_mount', 'report'
    ]

    def __init__(self, board):
        self.board = board

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
                devnode = self.board.hub.get_part()['devnode']
        if devnode:
            self.board.storage.unmount_host(devnode)
        else:
            self.board.log("Cannot find block device. Continuing anyway")

        self.board.storage.to_board()

    def pre_board_on(self):
        self.board.log("\n=== PRE BOARD ON ===", colour='blue', bold=True)

    def _board_on_and_validate(self):
        self.board.log("\n=!= BOARD ON AND VALIDATE =!=", bold=True)
        try:
            self.board.reboot_and_validate()
        except BootValidationError as e:
            raise TaskFailed(str(e))

    def pre_board_login(self):
        self.board.log("\n=== PRE BOARD LOGIN ===", colour='blue', bold=True)

    def _board_login(self):
        self.board.log("\n=!= BOARD LOGIN =!=", bold=True)
        try:
            self.board.login()
        except LoginFailed as e:
            raise TaskFailed(str(e))

    def pre_board_mount(self):
        self.board.log("\n=== PRE BOARD MOUNT ===", colour='blue', bold=True)

    def _board_mount(self):
        self.board.log("\n=!= BOARD MOUNT =!=", bold=True)
        self.board.storage.to_board()
        self.board.storage.mount_board()

    def post_board_mount(self):
        self.board.log("\n=== POST BOARD MOUNT ===", colour='blue', bold=True)

    def test_body(self):
        self.board.log("\n=== TEST BODY ===", colour='blue', bold=True)

    def pre_board_unmount(self):
        self.board.log("\n=== PRE BOARD UNMOUNT ===", colour='blue', bold=True)

    def _board_unmount(self):
        self.board.log("\n=!= BOARD UNMOUNT =!=", bold=True)
        self.board.storage.unmount_board()

    def _board_off(self):
        self.board.log("\n=!= BOARD OFF =!=", bold=True)
        self.board.power.off()

    def post_board_off(self):
        self.board.log("\n=== POST BOARD OFF ===", colour='blue', bold=True)

    def _host_mount(self):
        self.board.log("\n=!= HOST MOUNT =!=", bold=True)
        self.board.storage.to_host()

        devnode = None
        for _ in range(1, 5):
            if not self.board.hub.get_part():
                time.sleep(1)
            else:
                devnode = self.board.hub.get_part()['devnode']
        if not devnode:
            raise TaskFailed('Cannot mount: No block device partition downstream of hub')

        self.board.storage.mount_host(devnode)

    def report(self):
        self.board.log("\n=== REPORT ===", colour='blue', bold=True)


class TestRunner():
    def __init__(self, board, tests=None):
        self.board = board
        self.tests = []
        tests = tests or []
        if not isinstance(tests, list):
            tests = [tests]

        self.tasks = TestCore.tasks
        self.use_testcore = True

        # General purpose data for use globally between tests
        self.data = {}
        for test in tests:
            self.add_test(test)

    def __call__(self):
        self.run()

    def run(self):
        if (self.use_testcore and "TestCore" not in
                (_test_name(t) for t in self.tests)):
            self.add_test(TestCore(self.board), 0)

        self.board.log("Running tests: {}".format(
            list(map(lambda t: t.__class__.__name__, self.tests))))

        for task in self.tasks:
            self._run_task(task)

        self.board.log("\n== ALL TESTS COMPLETED ==", colour='blue', bold=True)

    def add_test(self, test, index=None):
        if index is None:
            self.board.log("Appending test: {}".format(_test_name(test)))
            self.tests.append(test)
        else:
            self.board.log("Inserting test at position {}: {} ".format(
                index, _test_name(test)))
            self.tests.insert(index, test)

    def rm_test(self, test):
        if test in self.tests:
            self.board.log("Removed test: {}".format(_test_name(test)))
            self.tests.remove(test)

    def _run_task(self, task_name):
        if "mount" in task_name and not self.board.storage:
            self.board.log("Board does not have storage. Skipping task: {}".format(task_name))
            return

        for test in self.tests:
            task_func = getattr(test, task_name, None)
            if task_func:
                if test.__class__ != TestCore:
                    self.board.log("Running: {} - {}".format(
                        _test_name(test), task_name))
                try:
                    task_func()
                except TaskFailed as e:
                    test.tasks_failed.append({
                        'name': task_name,
                        'cause': str(e),
                        'trace': traceback.format_exc()
                        })
                    self.send_fail_email(test)
                    self.board.log("Task failed: {} - {}: {}".format(
                        _test_name(test), task_name, str(e)))
                    if 'report' in self.tasks:
                        if task_name == 'report':
                            raise e
                        else:
                            self._run_task('report')
                            sys.exit(1)


    def send_fail_email(self, test):
        lab_maintainers = ['mwebster@witekio.com']
        email = Email(
            sender='lab@witekio.com',
            to=lab_maintainers,
            files=self.board.log_file,
            body='',
            body_type='html'
        )

        email.subject = 'Testing Failed: {} [{}] [{}]'.format(
            [_test_name(t) for t in self.tests],
            self.board.name, datetime.datetime.now()
        )
        email.body += '''
            <b>Platform: </b>{}<br><hr>
            '''.format('<br>'.join(list(str(platform.uname()).split(','))))

        for task in test.tasks_failed:
                email.body += '''
                    <b>Failed:</b> {}<br>
                    <b>Cause:</b> {}<br>
                    <b>Trace:</b> {}<br>
                    <hr>
                    '''.format(task['name'], task['cause'],
                    '<br>'.join(task['trace'].split('\n')))
        email.body += '<b>Board Info:</b><br>'
        email.body += '<br>'.join(self.board.show_hier().split('\n'))
        email.body += '<hr><br>'

        self.board.log(email.subject)
        self.board.log('Informing lab maintainers via email')

        email.send()

def _test_name(test):
    return test.__class__.__name__
