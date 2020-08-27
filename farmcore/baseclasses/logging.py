import datetime
import os

from enum import Enum, IntEnum
from farmutils import datetime_to_timestamp

from .hierarchy import hier_setter
from .singleton import Singleton

""" Enable logging """
DEFAULT_LOG_ON = True

""" Echo log to stdout """
DEFAULT_LOG_ECHO = True

""" Add hierarchical path to logs """
DEFAULT_LOG_HIER_PATH = False

""" Time format string """
DEFAULT_LOG_TIME_FORMAT = "%d-%m-%y %H:%M:%S"

""" Add timestamp to logs """
DEFAULT_LOG_TIME = False

""" Add log name to logs """
DEFAULT_LOG_NAME = None

COLOR_STYLES = {
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'purple': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[3m'
}
STYLE_NORMAL = '\033[0m'
STYLE_BOLD = '\033[1m'


class LogLevel(IntEnum):
    _MAX = 6
    ERROR = 5
    IMPORTANT = 4
    WARNING = 3
    INFO = 2
    NOTICE = 1
    DEBUG = 0


class LogMode(Enum):
    SILENT = 0
    QUIET = 1
    NORMAL = 2
    VERBOSE = 3
    DEBUG = 4

    def min_level(self) -> LogLevel:
        if self == LogMode.SILENT:
            return int(LogLevel._MAX)
        if self == LogMode.QUIET:
            return int(LogLevel.IMPORTANT)
        if self == LogMode.NORMAL:
            return int(LogLevel.INFO)
        if self == LogMode.VERBOSE:
            return int(LogLevel.NOTICE)
        if self == LogMode.DEBUG:
            return int(LogLevel.DEBUG)


class Logger(Singleton):
    '''Global log manager for the standard output.

    Handles the text formatting and what to output
    based on log levels and log mode.
    '''

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.mode = LogMode.NORMAL
        self.held = False
        self.log_buffer = ''

    def log(self, message, color=None, bold=False, newline=True, bypass_hold=False, level=None):
        if level is None:
            level = LogLevel.NOTICE

        if level < self.mode.min_level():
            return

        self._log(message, color, bold, newline, bypass_hold)

    def debug(self, message):
        self.log(message, level=LogLevel.DEBUG)

    def notice(self, message):
        self.log(message, level=LogLevel.NOTICE)

    def info(self, message):
        self.log(message, level=LogLevel.INFO)

    def warning(self, message):
        self.log(message, color='yellow', level=LogLevel.WARNING)

    def important(self, message):
        self.log(message, level=LogLevel.IMPORTANT)

    def error(self, message):
        self.log(message, color='red', level=LogLevel.ERROR)

    def _log(self, message, color=None, bold=False, newline=True, bypass_hold=False):
        style_reset = STYLE_NORMAL
        if color:
            if color in COLOR_STYLES:
                message = f'{COLOR_STYLES[color]}{message}{style_reset}'
                style_reset = ''
            else:
                raise ValueError(
                    f'Invalid color {color}. Supported colors: {COLOR_STYLES}')

        if bold:
            message = f'{STYLE_BOLD}{message}{style_reset}'

        if newline:
            message += os.linesep

        if self.held and not bypass_hold:
            self.log_buffer += message
        else:
            print(message, end='', flush=not newline)

    def hold(self):
        '''Hold the log output until `release` is called.'''
        self.held = True

    def release(self):
        '''Flush the log, and restore log output to normal.'''
        self.held = False
        if self.log_buffer:
            self._log(self.log_buffer)
        self.log_buffer = ''


class Logging():
    def __init__(self):
        if type(self) is Logging:
            raise AttributeError(
                'This is a base class, and must be inherited')

    @property
    def log_on(self):
        log = Logger()
        return log.mode != LogMode.SILENT

    @log_on.setter
    @hier_setter
    def log_on(self, log_on):
        log = Logger()
        if log_on is False:
            log.mode = LogMode.SILENT

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
        if not hasattr(self, "_log_file"):
            # Default logfile for all farmclasses lives in /tmp
            self._log_file = os.path.join('/tmp', 'lab', '{}_{}.log'.format(
                self.__class__.__name__, datetime_to_timestamp(datetime.datetime.now())))
        return self._log_file

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

    def log_file_clear(self):
        if self.log_file:
            open(self.log_file, 'w').close()

    def log(self, message, color=None, bold=False, force_echo=None,
            force_log_file=False, newline=True, bypass_hold=False, level=None):
        prefix = ''

        if force_echo is not None:
            echo = force_echo
        else:
            echo = self.log_echo

        if force_log_file is not False:
            log_file = force_log_file
        else:
            log_file = self.log_file

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
            if log_file:
                logdir = os.path.dirname(log_file)
                if logdir and not os.path.exists(logdir):
                    os.makedirs(logdir)
                with open(log_file, 'a', encoding='utf-8') as logfd:
                    logfd.write(message + '\n')

            if echo:
                logger = Logger()
                logger.log(message.replace('\\n', '\n'), color=color, bold=bold,
                           newline=newline, bypass_hold=bypass_hold, level=level)

    def hold_log(self):
        global_log = Logger()
        global_log.hold()

    def release_log(self):
        global_log = Logger()
        global_log.release()

    def error(self, message, exception=None):
        message = f'ERROR: {message}'
        self.log(message, color='red', bold=True)
        if exception:
            raise exception(message)
