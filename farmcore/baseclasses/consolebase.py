import time
import pexpect
import pexpect.fdpexpect
import json
import os
from datetime import datetime
from abc import ABCMeta, abstractmethod
from functools import wraps

from farmutils import datetime_to_timestamp

from .farmclass import Farmclass


DEFAULT_PROMPT = r'>>FARM>>'


class ConsoleError(Exception):
    pass


class ConsoleCannotOpenError(ConsoleError):
    pass


class ConsoleLoginFailedError(ConsoleError):
    pass


class ConsoleExceptionKeywordRecievedError(ConsoleError):
    pass


class ConsoleInvalidJSONRecievedError(ConsoleError):
    pass


class ConsoleBase(Farmclass, metaclass=ABCMeta):
    """ Impliments the console functionality not specific to a given transport layer """

    def __init__(self, encoding=None, linesep=None, raw_logfile=None):
        if not hasattr(self, '_pex'):
            raise AttributeError(
                "Variable '_pex' must be created by inheriting class")

        default_raw_logfile = os.path.join('/tmp', 'lab', '{}_raw_{}.log'.format(
                self.__class__.__name__, datetime_to_timestamp(datetime.now())
        ))

        self.encoding = encoding or 'ascii'
        self.linesep = linesep or '\r\n'
        self.raw_logfile = raw_logfile or default_raw_logfile

        self._buffer = ''
        self._last_recieved = ''
        self._raw_logfile_fd = None

    @property
    @abstractmethod
    def is_open(self):
        """ Check if the transport layer is ready to send and receive"""
        pass
        
    @abstractmethod
    def open(f):
        @wraps(f)
        def wrap(self):
            f(self)
            if self.raw_logfile:
                # Create raw_logfile dir if it does not already exist
                os.makedirs(os.path.dirname(self.raw_logfile), exist_ok=True)

                self._raw_logfile_fd = open(self.raw_logfile, 'ab')
                self._pex.logfile=self._raw_logfile_fd
        return wrap

    @abstractmethod
    def close(f):
        @wraps(f)
        def wrap(self):
            f(self)
            if self._raw_logfile_fd:
                self._raw_logfile_fd.close()
                self._raw_logfile_fd = None
        return wrap

    def raw_logfile_clear(self):
        open(self.raw_logfile, 'w').close()

    def flush(self, clear_buf=False):
        if not self.is_open:
            self.open()
        try:
            while 1:
                last_read = self.decode(self._pex.read_nonblocking(1, 0.01))
                self._buffer += last_read
        except pexpect.exceptions.TIMEOUT:
            pass
        except pexpect.exceptions.EOF:
            pass

        if clear_buf:
            if self._buffer.strip():
                self.log('<<flushed>>{}<</flushed>>'.format(self._buffer),
                    force_echo=False)
            self._buffer = ''
        return self._buffer

    @property
    def _buffer_size(self):
        return len(self._buffer)

    def _flush_get_size(self, clear_buf=False):
        self.flush(clear_buf)
        return self._buffer_size

    def decode(self, text):
        return text.decode(self.encoding, 'replace')

    def encode(self, text):
        return text.encode(self.encoding)

    def wait_for_data(
            self, timeout=None, sleep_time=None,
            match=None, start_bytes=None, verbose=None):

        timeout = timeout or 10.0
        sleep_time = sleep_time or 0.1
        verbose = verbose or True

        if match:
            return self.wait_for_match(
                match=match,
                timeout=timeout,
                verbose=verbose
            )
        else:
            return self.wait_for_bytes(
                timeout=timeout,
                sleep_time=sleep_time,
                start_bytes=start_bytes,
                verbose=verbose
            )

    def wait_for_match(self, match, timeout, verbose=None):
        verbose = verbose or False

        retval = False

        old_timeout = self._pex.timeout
        self._pex.timeout = timeout

        if not self.is_open:
            self.open()

        if not isinstance(match, list):
            match = [match]
        watches = [pexpect.TIMEOUT, pexpect.EOF] + match

        if verbose:
            self.log("Waiting up to {}s for patterns: {}...".format(
                timeout, match))

        matched = watches[self._pex.expect(watches)]
        if matched in match:
            retval = self.decode(self._pex.after)

        self._pex.timeout = old_timeout

        return retval

    def wait_for_bytes(
            self, timeout=None, sleep_time=None,
            start_bytes=None, verbose=None):

        timeout = timeout or 10.0
        sleep_time = sleep_time or 0.1
        verbose = verbose or True

        if not self.is_open:
            self.open()

        self.flush()
        if start_bytes is None:
            start_bytes = self._flush_get_size()

        elapsed = 0.0

        while(elapsed < timeout):
            current_bytes = self._flush_get_size()
            if verbose:
                self.log("Waiting for data: Waited[{:.1f}/{:.1f}s] Recieved[{:.0f}B]...".format(
                    elapsed, timeout, current_bytes-start_bytes))
            if current_bytes > start_bytes:
                return True

            time.sleep(sleep_time)
            elapsed += sleep_time

        return False

    def wait_for_quiet(self, timeout=10.0, quiet=0.3, sleep_time=0.1, verbose=True):
        if not self.is_open:
            self.open()

        time_quiet = 0.0
        elapsed = 0.0

        last_bytes = 0

        current_bytes = self._flush_get_size(False)
        while(elapsed < timeout):
            current_bytes = self._flush_get_size(False)

            if current_bytes == last_bytes:
                time_quiet += sleep_time
            else:
                time_quiet = 0

            if verbose:
                self.log("Waiting for quiet... Waited[{:.1f}/{:.1f}s] Quiet[{:.1f}/{:.1f}s] Recieved[{:.0f}B]...".format(
                    elapsed, timeout, time_quiet, quiet, current_bytes
                    ))

            if time_quiet > quiet:
                return True

            last_bytes = self._flush_get_size(False)

            time.sleep(sleep_time)
            elapsed += sleep_time

        return False

    def send(self,
             cmd=None,
             recieve=False,
             match=None,
             excepts=None,
             send_newline=True,
             log_verbose=True,
             timeout=-1,
             sleep_time=-1,
             quiet_time=-1,
             flush_buffer=True
             ):
        if not self.is_open:
            self.open()
        if not self.is_open:
            raise ConsoleCannotOpenError

        cmd = cmd or ''
        if log_verbose:
            self.log("Sending command:\n{}".format(cmd), force_log_file=None)

        if isinstance(cmd, str):
            cmd = self.encode(cmd)

        recieved = None
        matched = False

        match = match or []
        excepts = excepts or []
        watches = []

        if not isinstance(match, list):
            match = [match]

        if not isinstance(excepts, list):
            excepts = [excepts]

        watches.extend(match)
        watches.extend(excepts)

        """ Assign default timeout and sleep values if unassigned """
        data_timeout = timeout if timeout >= 0 else 5
        quiet_timeout = timeout if timeout >= 0 else 3
        data_sleep = sleep_time if sleep_time >= 0 else 0.1
        quiet_sleep = sleep_time if sleep_time >= 0 else 0.1
        quiet_time = quiet_time if quiet_time >= 0 else 0.3

        self._pex.linesep = self.encode(self.linesep)

        if flush_buffer:
            self.flush(True)

        if not recieve and not watches:
            if send_newline:
                self._pex.sendline(cmd)
            else:
                self._pex.send(cmd)

            self.log('<<sent>>{}<</sent>>'.format(cmd), force_echo=False)

            return (None, None)
        else:
            if send_newline:
                self._pex.sendline(cmd)
            else:
                self._pex.send(cmd)

            self.log('<<sent>>{}<</sent>>'.format(cmd), force_echo=False)

            if watches:
                matched = self.wait_for_data(
                    timeout=data_timeout,
                    match=watches,
                    verbose=log_verbose)
                recieved = self.decode(self._pex.before)
                new_recieved = recieved[len(self._last_recieved):]
                if matched:
                    self._last_recieved = ''
                    match_str = '<<matched expects={}>>{}<</matched>>'.format(
                        watches, matched)
                else:
                    self._last_recieved = recieved
                    match_str = '<<not_matched expects={}>>'.format(watches)
                self.log("<<recieved>>{}{}<</recieved>>".format(
                    new_recieved, match_str), force_echo=False)
                if matched in excepts:
                    self.error('Matched [{}] is in exceptions list {}'.format(
                        matched, excepts), exception=ConsoleExceptionKeywordRecievedError)
                return (recieved, matched)
            else:
                self.wait_for_quiet(
                    timeout=quiet_timeout,
                    sleep_time=quiet_sleep,
                    quiet=quiet_time,
                    verbose=log_verbose)
                recieved = self._buffer
                return (recieved, None)

    def check_alive(self, timeout=10.0):
        start_bytes = self._flush_get_size()
        self.send("")
        alive = self.wait_for_data(timeout=timeout, start_bytes=start_bytes)

        if alive:
            self.log("Got response from: {}".format(self))
        else:
            self.log("No response from: {}".format(self))
        return alive

    def login(self, username, username_match,
              password=None, password_match=None, success_match=None):
        matches = [username_match]
        if password and password_match:
            matches.append(password_match)
        if success_match:
            matches.append(success_match)

        fail_message = "ERROR: Failed to log in: U={} P={}".format(
            username, password)

        (__, matched) = self.send(
            match=matches, send_newline=False, flush_buffer=False)
        if not matched:
            self.error(fail_message, ConsoleLoginFailedError)

        if matched == username_match:
            (__, matched) = self.send(
                cmd=username, match=matches, flush_buffer=False)
            if matched == username_match:
                self.error(
                    '{}: Invalid username'.format(fail_message),
                    ConsoleLoginFailedError)

        if password_match and matched == password_match:
            if not password:
                self.error(fail_message, ConsoleLoginFailedError)
            (__, matched) = self.send(
                cmd=password,  match=matches, flush_buffer=False)
            if matched == password_match or matched == username_match:
                self.error(fail_message, ConsoleLoginFailedError)

        if ((success_match and matched != success_match) or
                matched == pexpect.TIMEOUT or
                matched == pexpect.EOF):
            self.error(fail_message, ConsoleLoginFailedError)

        if (success_match and matched == success_match):
            self.log('Login successful')

    def get_json_data(self, cmd):
        ''' Execute a command @cmd on target which generates JSON data.
        Parse this data, and return a dict of it.'''

        self.wait_for_quiet(quiet=1, sleep_time=0.5)
        recieved, matched = self.send(cmd, match='{((.|\n)*)\n}')

        if not matched:
            raise ConsoleInvalidJSONRecievedError(
                f'Received is not JSON: {recieved}')

        data = json.loads(matched)
        return data
