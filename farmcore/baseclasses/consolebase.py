import time
import pexpect
import pexpect.fdpexpect
import json
import os

from deprecated import deprecated
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


class ConsoleExceptionKeywordReceivedError(ConsoleError):
    pass


class ConsoleInvalidJSONReceivedError(ConsoleError):
    pass


class ConsoleBase(Farmclass, metaclass=ABCMeta):
    """ Implements the console functionality not specific to a given transport layer """

    def __init__(self, encoding=None, linesep=None, raw_logfile=None):
        if not hasattr(self, '_pex'):
            raise AttributeError(
                "Variable '_pex' must be created by inheriting class")

        timestamp = datetime_to_timestamp(datetime.now())
        default_raw_logfile = os.path.join(
            '/tmp', 'lab',
            f'{self.__class__.__name__}_raw_{timestamp}.log')

        self.encoding = encoding or 'ascii'
        self.linesep = linesep or '\n'
        self.raw_logfile = raw_logfile or default_raw_logfile

        self._buffer = ''
        self._last_received = ''
        self._raw_logfile_fd = None
        self._pex = None

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
                self._pex.logfile = self._raw_logfile_fd
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
                self.log(
                    f'<<flushed>>{self._buffer}<</flushed>>', force_echo=False)
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

    @deprecated(version='2.0', reason='You should use "wait_for_bytes" or "wait_for_quiet" instead')
    def wait_for_data(
            self, timeout=None, sleep_time=None,
            match=None, start_bytes=None, verbose=None):

        timeout = timeout or 10.0
        sleep_time = sleep_time or 0.1
        verbose = verbose if verbose is not None else False

        if match:
            return self._wait_for_match(
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

    def wait_for_match(self, match, timeout=None, verbose=None):
        verbose = verbose or False
        timeout = timeout or self._pex.timeout

        if not self.is_open:
            self.open()

        if not isinstance(match, list):
            match = [match]

        if verbose:
            self.log(f'Waiting up to {timeout}s for patterns: {match}...')

        matched_str = None
        try:
            index = self._pex.expect(match, timeout)
            matched_str = match[index]
        except pexpect.EOF:
            pass
        except pexpect.TIMEOUT:
            pass

        if verbose:
            if matched_str:
                self.log(f'Matched {matched_str}')
            else:
                self.log(f'No match found before timeout or EOF')

        return matched_str

    @deprecated(version='2.0', reason='You should use "wait_for_match" instead')
    def _wait_for_match(self, match, timeout, verbose=None):
        verbose = verbose or False

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
        self._pex.timeout = old_timeout

        # Pexpect child `.after` is the text matched after calling `.expect`
        if matched in match:
            return self.decode(self._pex.after)

        return False

    def wait_for_bytes(
            self, timeout=None, sleep_time=None,
            start_bytes=None, verbose=None):
        timeout = timeout or 10.0
        sleep_time = sleep_time or 0.1
        verbose = verbose or False

        if not self.is_open:
            self.open()

        self.flush()
        if start_bytes is None:
            start_bytes = self._flush_get_size()

        elapsed = 0.0

        while(elapsed < timeout):
            current_bytes = self._flush_get_size()
            if verbose:
                self.log("Waiting for data: Waited[{:.1f}/{:.1f}s] Received[{:.0f}B]...".format(
                    elapsed, timeout, current_bytes-start_bytes))
            if current_bytes > start_bytes:
                return True

            time.sleep(sleep_time)
            elapsed += sleep_time

        return False

    def wait_for_quiet(self, timeout=None, quiet=None, sleep_time=None, verbose=False):
        if not self.is_open:
            self.open()

        timeout = timeout if timeout is not None else 10.0
        quiet = quiet if quiet is not None else 0.3
        sleep_time = sleep_time if sleep_time is not None else 0.1
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
                self.log("Waiting for quiet... Waited[{:.1f}/{:.1f}s] Quiet[{:.1f}/{:.1f}s] Received[{:.0f}B]...".format(
                    elapsed, timeout, time_quiet, quiet, current_bytes
                ))

            if time_quiet > quiet:
                return True

            last_bytes = self._flush_get_size(False)

            time.sleep(sleep_time)
            elapsed += sleep_time

        return False

    @deprecated(version='2.0', reason='You should use "send_nonblocking" instead')
    def send(self,
             cmd=None,
             receive=False,
             match=None,
             excepts=None,
             send_newline=True,
             log_verbose=True,
             timeout=None,
             sleep_time=None,
             quiet_time=None,
             flush_buffer=True
             ):
        if not self.is_open:
            self.open()
        if not self.is_open:
            raise ConsoleCannotOpenError

        cmd = cmd or ''
        if log_verbose:
            self.log(f"Sending command:\n    {cmd}", force_log_file=None)

        if isinstance(cmd, str):
            cmd = self.encode(cmd)

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
        data_timeout = timeout if timeout is not None else 5
        quiet_timeout = timeout if timeout is not None else 3
        quiet_sleep = sleep_time if sleep_time is not None else 0.1
        quiet_time = quiet_time if quiet_time is not None else 0.3

        self._pex.linesep = self.encode(self.linesep)

        if flush_buffer:
            self.flush(True)

        received = None
        matched = None
        if not receive and not watches:
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
                received = self.decode(self._pex.before)
                new_received = received[len(self._last_received):]
                if matched:
                    self._last_received = ''
                    match_str = '<<matched expects={}>>{}<</matched>>'.format(
                        watches, matched)
                else:
                    self._last_received = received
                    match_str = '<<not_matched expects={}>>'.format(watches)
                self.log("<<received>>{}{}<</received>>".format(
                    new_received, match_str), force_echo=False)
                if matched in excepts:
                    self.error('Matched [{}] is in exceptions list {}'.format(
                        matched, excepts), exception=ConsoleExceptionKeywordReceivedError)
            else:
                self.wait_for_quiet(
                    timeout=quiet_timeout,
                    sleep_time=quiet_sleep,
                    quiet=quiet_time,
                    verbose=log_verbose)
                received = self._buffer

        return (received, matched)

    def send_and_read(self,
                      cmd,
                      timeout=None,
                      sleep_time=None,
                      quiet_time=None,
                      send_newline=True,
                      flush_before=True,
                      verbose=False):
        quiet_timeout = timeout if timeout is not None else 3
        quiet_sleep = sleep_time if sleep_time is not None else 0.1
        quiet_time = quiet_time if quiet_time is not None else 0.3

        self.send_nonblocking(cmd, send_newline=send_newline,
                              verbose=verbose, flush_before=flush_before)

        self.wait_for_quiet(
            timeout=quiet_timeout,
            sleep_time=quiet_sleep,
            quiet=quiet_time,
            verbose=verbose)
        received = self._buffer

        return received

    def send_and_expect(self,
                        cmd,
                        match,
                        excepts=None,
                        timeout=None,
                        send_newline=True,
                        flush_before=True,
                        verbose=False):

        match = match or []
        excepts = excepts or []
        timeout = timeout if timeout is not None else 5

        if not isinstance(match, list):
            match = [match]
        if not isinstance(excepts, list):
            excepts = [excepts]

        watches = []
        watches.extend(match)
        watches.extend(excepts)

        self.send_nonblocking(cmd, send_newline=send_newline,
                              verbose=verbose, flush_before=flush_before)

        matched = self.wait_for_match(
            timeout=timeout,
            match=watches,
            verbose=verbose)
        received = self.decode(self._pex.before)
        new_received = received[len(self._last_received):]

        if matched:
            self._last_received = ''
            match_str = f'<<matched expects={watches}>>{matched}<</matched>>'
        else:
            self._last_received = received
            match_str = f'<<not_matched expects={watches}>>'

        self.log(
            f'<<received>>{new_received}{match_str}<</received>>', force_echo=False)

        if matched in excepts:
            self.error(f'Matched [{matched}] is in exceptions list {excepts}',
                       exception=ConsoleExceptionKeywordReceivedError)

        return (received, matched)

    def send_nonblocking(self, cmd,
                         send_newline=True,
                         flush_before=True,
                         verbose=False
                         ):

        if not self.is_open:
            self.open()
        if not self.is_open:
            raise ConsoleCannotOpenError

        cmd = cmd or ''
        if verbose:
            self.log(f'Sending command: \'{cmd}\'', force_log_file=None)

        if isinstance(cmd, str):
            cmd = self.encode(cmd)

        self._pex.linesep = self.encode(self.linesep)

        if flush_before:
            self.flush(True)

        if send_newline:
            self._pex.sendline(cmd)
        else:
            self._pex.send(cmd)

        self.log(f'<<sent>>{cmd}<</sent>>', force_echo=False)

    def check_alive(self, timeout=10.0):
        start_bytes = self._flush_get_size()
        self.send_and_read('')
        alive = self.wait_for_bytes(timeout=timeout, start_bytes=start_bytes)

        if alive:
            self.log(f'Got response from: {self}')
        else:
            self.log(f'No response from: {self}')

        return alive

    def login(self, username, username_match,
              password=None, password_match=None, success_match=None):
        matches = [username_match]
        if password_match:
            matches.append(password_match)
        if success_match:
            matches.append(success_match)

        fail_message = f'ERROR: Failed to log in: U="{username}" P="{password}"'
        (__, matched) = self.send_and_expect('', match=matches)
        if not matched:
            self.error(fail_message, ConsoleLoginFailedError)

        if matched == username_match:
            matches.remove(username_match)
            (__, matched) = self.send_and_expect(cmd=username,
                                                 match=matches)
            self.wait_for_quiet()

        if password_match and matched == password_match:
            if not password:
                self.error(f'{fail_message}: No password set, but password prompt detected',
                           ConsoleLoginFailedError)

            matches.remove(password_match)
            (__, matched) = self.send_and_expect(cmd=password,
                                                 match=matches)
            self.wait_for_quiet()

        if ((success_match and matched != success_match) or
                matched in [pexpect.TIMEOUT, pexpect.EOF]):
            self.error(fail_message, ConsoleLoginFailedError)

        self.log('Login successful')

    def get_json_data(self, cmd):
        ''' Execute a command @cmd on target which generates JSON data.
        Parse this data, and return a dict of it.'''

        self.wait_for_quiet(quiet=1, sleep_time=0.5)
        received, matched = self.send_and_expect(cmd, match='{((.|\n)*)\n}')

        if not matched:
            raise ConsoleInvalidJSONReceivedError(
                f'Received is not JSON: {received}')

        data = json.loads(matched)
        return data

    def support_file_copy(self):
        return False

    def copy_to_target(self, source, destination, timeout=30):
        raise ValueError(
            f'Console type {self} does not support copying to target')

    def copy_to_host(self, source, destination, timeout=30):
        raise ValueError(
            f'Console type {self} does not support copying from target')
