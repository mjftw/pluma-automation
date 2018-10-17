import datetime
import os

from .hierachy import hier_setter


""" Enable logging """
DEFAULT_LOG_ON = True

""" Echo log to stdout """
DEFAULT_LOG_ECHO = True

""" Add hierachial path to logs """
DEFAULT_LOG_HIER_PATH = False

""" Time format string """
DEFAULT_LOG_TIME_FORMAT = "%y-%m-%d %H:%M:%S"

""" Add timestamp to logs """
DEFAULT_LOG_TIME = False

""" Add log name to logs """
DEFAULT_LOG_NAME = None

""" Log file to write to """
DEFAULT_LOG_FILE = None


class Logging():
    @property
    def log_on(self):
        if hasattr(self, "_log_on"):
            return self._log_on
        else:
            return DEFAULT_LOG_ON

    @log_on.setter
    @hier_setter
    def log_on(self, log_on):
        self._log_on = log_on

    @property
    def log_name(self):
        if hasattr(self, "_log_name"):
            return self._log_name
        else:
            return DEFAULT_LOG_NAME

    @log_name.setter
    @hier_setter
    def log_name(self, log_name):
        self._log_name = log_name

    @property
    def log_time(self):
        if hasattr(self, "_log_time"):
            return self._log_time
        else:
            return DEFAULT_LOG_TIME

    @log_time.setter
    @hier_setter
    def log_time(self, log_time):
        self._log_time = log_time

    @property
    def log_time_format(self):
        if hasattr(self, "_log_time_format"):
            return self._log_time_format
        else:
            return DEFAULT_LOG_TIME_FORMAT

    @log_time_format.setter
    @hier_setter
    def log_time_format(self, log_time_format):
        self._log_time_format = log_time_format

    @property
    def log_file(self):
        if hasattr(self, "_log_file"):
            return self._log_file
        else:
            return DEFAULT_LOG_FILE

    @log_file.setter
    @hier_setter
    def log_file(self, log_file):
        self._log_file = log_file

    @property
    def log_echo(self):
        if hasattr(self, "_log_echo"):
            return self._log_echo
        else:
            return DEFAULT_LOG_ECHO

    @log_echo.setter
    @hier_setter
    def log_echo(self, log_echo):
        self._log_echo = log_echo

    @property
    def log_hier_path(self):
        if hasattr(self, "_log_hier_path"):
            return self._log_hier_path
        else:
            return DEFAULT_LOG_HIER_PATH

    @log_hier_path.setter
    @hier_setter
    def log_hier_path(self, log_hier_path):
        if log_hier_path:
            if isinstance(log_hier_path, bool):
                self._log_hier_path = '{}'.format(type(self).__name__)
            else:
                self._log_hier_path = '{}.{}'.format(
                        log_hier_path, type(self).__name__)
        else:
            self._log_hier_path = False

    def log(self, message):
        prefix = ''
        if self.log_on:
            if self.log_hier_path:
                prefix = '[{}]{}'.format(self.log_hier_path, prefix)
            if self.log_name:
                prefix = '{}{}'.format(self.log_name, prefix)
            if self.log_time and self.log_time_format:
                timestr = datetime.datetime.now().strftime(self.log_time_format)
                prefix = '{} {}'.format(timestr, prefix)
            if prefix:
                message = '{}: {}'.format(prefix, message)
            if self.log_file:
                logdir = os.path.dirname(self.log_file)
                if logdir and not os.path.exists(logdir):
                    os.makedirs(logdir)
                with open(self.log_file, 'a') as logfd:
                    logfd.write(message + '\n')
            if self.log_echo:
                print(message)
