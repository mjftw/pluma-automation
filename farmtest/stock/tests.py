import os
from datetime import datetime
from copy import copy

from farmutils import datetime_to_timestamp

from ..test import TestBase, BootTestBase


class StockBootTest(BootTestBase):
    def __init__(self, board, console_log_file, failed_logs_dir):
        super().__init__(self)
        self.board = board
        self.console_log_file = console_log_file
        self.failed_logs_dir = failed_logs_dir

        self.start_datetime = None

    def prepare(self):
        if not os.path.exists(self.failed_logs_dir):
            os.mkdir(self.failed_logs_dir)

        self.start_datetime = datetime.now()

        self.board.console.log_file = self.console_log_file
        self.board.console.log_file_clear()

    def report(self):
        self.data['boot_success'] = self.boot_success

        if self.boot_success:
            self.board.log('Successful boot in {}s'.format(
                self.board.last_boot_len))

            self.data['boot_time'] = self.board.last_boot_len
        else:
            logfile_timestamp = datetime_to_timestamp(self.start_datetime)

            new_logfile_path = os.path.join(
                self.failed_logs_dir, 'console_{}.log'.format(
                    logfile_timestamp))

            self.board.error('Boot failed! Saving console log to {}'.format(
                new_logfile_path))
            os.rename(self.board.console.log_file, new_logfile_path)

            self.data['console_log'] = new_logfile_path


class StockSensorsTest(TestBase):
    def __init__(self, board):
        super().__init__(self)
        self.board = board

    def test_body(self):
        #TODO: Add check that board has command sensors (from lm-sensors), with json option
        self.data['sensors'] = self.board.console.get_json_data('sensors -j')

