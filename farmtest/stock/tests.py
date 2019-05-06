import os
from datetime import datetime
from copy import copy

from ..test import BootTestBase


class StockBootTest(BootTestBase):
    def __init__(self, board, global_data, console_log_file, failed_logs_dir):
        super().__init__(self)
        self.board = board
        self.console_log_file = console_log_file
        self.failed_logs_dir = failed_logs_dir
        self.global_data = global_data

        self.start_datetime = None

        self.data_key = str(self)
        if (self.data_key not in self.global_data or
                not isinstance(list, self.global_data[self.data_key])):
            self.global_data[self.data_key] = []

    def prepare(self):
        if not os.path.exists(self.failed_logs_dir):
            os.mkdir(self.failed_logs_dir)

        self.start_datetime = datetime.now()

        self.board.console.log_file = self.console_log_file
        self.board.console.log_file_clear()

    def report(self):
        save_data = {
            'boot_success': copy(self.boot_success)
        }

        if self.boot_success:
            self.board.log('Successful boot in {}s'.format(
                self.board.last_boot_len))

            save_data['boot_time'] = copy(self.board.last_boot_len)
        else:
            logfile_format = '%Y_%m_%d_%H_%M_%S'
            logfile_timestamp = self.start_datetime.strftime(logfile_format)

            new_logfile_path = os.path.join(
                self.failed_logs_dir, 'console_{}.log'.format(
                    logfile_timestamp))

            self.board.error('Boot failed! Saving console log to {}'.format(
                new_logfile_path))
            os.rename(self.board.console.log_file, new_logfile_path)

            save_data['console_log'] = new_logfile_path

        self.global_data[self.data_key].append(save_data)
