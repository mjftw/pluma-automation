'''
class ExampleTest(TestBase):
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

import datetime
import time
import shutil
import os

from pluma.utils import datetime_to_timestamp
from pluma.core.exceptions import BoardBootValidationError, ConsoleLoginFailedError
from pluma.test import TestBase, TaskFailed


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
        self.board.log("\n=== PRE HOST MOUNT ===", color='blue', bold=True)

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
            raise TaskFailed(
                'Cannot mount: No block device partition downstream of hub')

        self.board.storage.mount_host(devnode)

    def prepare(self):
        self.board.log("\n=== PREPARE ===", color='blue', bold=True)

    def _host_unmount(self):
        self.board.log("\n=!= HOST UNMOUNT =!=", bold=True)

        # TODO: Move this functionality to the board class
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
            self.board.log(
                "Cannot find block device partition. Continuing anyway")

        self.board.storage.to_board()

    def pre_board_on(self):
        self.board.log("\n=== PRE BOARD ON ===", color='blue', bold=True)

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
                shutil.copy2(self.board.console.log_file,
                             self.data['boot_log'])
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
        self.board.log("\n=== PRE BOARD LOGIN ===", color='blue', bold=True)

    def _board_login(self):
        self.board.log("\n=!= BOARD LOGIN =!=", bold=True)
        try:
            self.board.login()
        except ConsoleLoginFailedError as e:
            raise TaskFailed(str(e))

    def pre_board_mount(self):
        self.board.log("\n=== PRE BOARD MOUNT ===", color='blue', bold=True)

    def _board_mount(self):
        self.board.log("\n=!= BOARD MOUNT =!=", bold=True)
        self.board.storage.to_board()
        self.board.storage.mount_board()

    def pre_test_body(self):
        self.board.log("\n=== PRE TEST BODY ===", color='blue', bold=True)

    def test_body(self):
        self.board.log("\n=== TEST BODY ===", color='blue', bold=True)

    def post_test_body(self):
        self.board.log("\n=== POST TEST BODY ===", color='blue', bold=True)

    def _board_unmount(self):
        self.board.log("\n=!= BOARD UNMOUNT =!=", bold=True)
        self.board.storage.unmount_board()

    def _board_off(self):
        self.board.log("\n=!= BOARD OFF =!=", bold=True)
        self.board.power.off()

    def post_board_off(self):
        self.board.log("\n=== POST BOARD OFF ===", color='blue', bold=True)

    def report(self):
        self.board.log("\n=== REPORT ===", color='blue', bold=True)
