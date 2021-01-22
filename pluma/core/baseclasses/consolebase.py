import time
import json
import os
from typing import Optional, List, Tuple, Union
from abc import ABC, abstractmethod

from pluma.core.dataclasses import SystemContext
from pluma.core.baseclasses import ConsoleEngine, PexpectEngine

from .hardwarebase import HardwareBase
from .logging import LogLevel
from .consoleexceptions import (ConsoleError, ConsoleCannotOpenError,
                                ConsoleExceptionKeywordReceivedError,
                                ConsoleInvalidJSONReceivedError,
                                ConsoleLoginFailedError)


class ConsoleBase(HardwareBase, ABC):
    """ Implements the console functionality not specific to a given transport layer """

    def __init__(self, encoding: str = None, linesep: str = None,
                 raw_logfile: str = None, system: SystemContext = None,
                 engine: ConsoleEngine = None):
        self.engine = engine or PexpectEngine(linesep=linesep,
                                              encoding=encoding,
                                              raw_logfile=raw_logfile)
        self.system = system or SystemContext()
        self._requires_login = True

    @abstractmethod
    def open(self):
        '''Open a console.'''

    def _on_opened(self):
        '''Executed after the console is opened.'''

    @property
    def is_open(self):
        '''Return whether the console is opened or not'''
        return self.engine.is_open

    def close(self):
        '''Close the console.'''
        self.engine.close()

    def _on_closed(self):
        '''Executed after the console is closed.'''

    def require_open(self):
        '''Open the console or raise an error.'''
        if not self.is_open:
            self.open()
        if not self.is_open:
            raise ConsoleCannotOpenError

    def read_all(self, preserve_read_buffer: bool = False) -> str:
        '''Read and return all data available on the console'''
        self.require_open()
        return self.engine.read_all(preserve_read_buffer=preserve_read_buffer)

    def wait_for_match(self, match: List[str], timeout=None) -> Optional[str]:
        '''Wait a maximum duration of 'timeout' for a matching regex, and returns matched text'''
        self.require_open()
        match_result = self.engine.wait_for_match(match=match, timeout=timeout)
        return match_result.text_matched

    def wait_for_bytes(self, timeout: Optional[float] = None,
                       sleep_time: Optional[float] = None,
                       start_bytes: int = None) -> bool:
        '''Wait for data to be received on the console.'''
        timeout = timeout if timeout is not None else 10.0
        sleep_time = sleep_time if sleep_time is not None else 0.1

        self.require_open()

        self.engine.read_all(preserve_read_buffer=True)
        initial_byte_count = start_bytes or self.engine.reception_buffer_size

        start_time = time.time()
        while(time.time()-start_time < timeout):
            self.engine.read_all(preserve_read_buffer=True)
            byte_count = self.engine.reception_buffer_size

            self.log(f'Waiting for data: Waited[{time.time()-start_time:.1f}/{timeout:.1f}s] '
                     'Received[{byte_count-initial_byte_count}B]...',
                     level=LogLevel.DEBUG)

            if byte_count > initial_byte_count:
                return True

            time.sleep(sleep_time)

        return False

    def wait_for_quiet(self, quiet: float = None, sleep_time: float = None,
                       timeout: float = None) -> bool:
        '''Wait at most "timeout" for no activity during "quiet" consecutive seconds'''
        self.require_open()
        quiet = quiet if quiet is not None else 0.5
        sleep_time = sleep_time if sleep_time is not None else 0.1
        timeout = timeout if timeout is not None else 10.0

        last_read_buffer_size = 0
        start = time.time()
        now = start
        quiet_start = start
        while(now - start < timeout):
            time.sleep(sleep_time)

            self.read_all(preserve_read_buffer=True)
            reception_buffer_size = self.engine.reception_buffer_size

            # Check if more data was received
            now = time.time()
            if reception_buffer_size == last_read_buffer_size:
                if now - quiet_start > quiet:
                    return True
            else:
                quiet_start = now

            last_read_buffer_size = reception_buffer_size
            log_string = ("Waiting for quiet... Waited[{:.1f}/{:.1f}s] "
                          "Quiet[{:.1f}/{:.1f}s] Received[{:.0f}B]...")
            self.log(log_string.format(now - start, timeout, now - quiet_start,
                                       quiet, reception_buffer_size), level=LogLevel.DEBUG)

        # Timeout
        return False

    def send_and_read(self, cmd: str, timeout: Optional[float] = None,
                      sleep_time: Optional[float] = None,
                      quiet_time: Optional[float] = None,
                      send_newline: bool = True, flush_before: bool = True) -> str:
        '''Send a command/data on the console, wait for quiet and return the data received'''
        timeout = timeout if timeout is not None else 3
        sleep_time = sleep_time if sleep_time is not None else 0.1
        quiet_time = quiet_time if quiet_time is not None else 0.3

        self.send_nonblocking(cmd, send_newline=send_newline,
                              flush_before=flush_before)
        self.wait_for_quiet(quiet=quiet_time, sleep_time=sleep_time,
                            timeout=timeout)
        return self.read_all()

    def send_and_expect(self, cmd: str, match: Union[str, List[str]],
                        excepts: Union[str, List[str]] = None,
                        timeout: int = None, send_newline: bool = True,
                        flush_before: bool = True) -> Tuple[str, Optional[str]]:
        '''Send a command/data on the console, and wait for one of "expects" patterns.'''
        match = match or []
        excepts = excepts or []
        timeout = timeout if timeout is not None else 5

        if isinstance(match, str):
            match = [match]
        if isinstance(excepts, str):
            excepts = [excepts]

        watches = []
        watches.extend(match)
        watches.extend(excepts)

        self.send_nonblocking(cmd, send_newline=send_newline,
                              flush_before=flush_before)

        result = self.engine.wait_for_match(timeout=timeout, match=watches)

        if result.regex_matched:
            debug_match_str = f'<<matched expects={watches}>>{result.regex_matched}<</matched>>'
        else:
            debug_match_str = f'<<not_matched expects={watches}>>'

        self.log(f'<<received>>{result.text_received}{debug_match_str}<</received>>',
                 force_echo=False, level=LogLevel.DEBUG)

        if result.regex_matched in excepts:
            self.error(f'Matched [{result.regex_matched}] is in exceptions list {excepts}',
                       exception=ConsoleExceptionKeywordReceivedError)

        return (result.text_received, result.text_matched)

    def send_nonblocking(self, cmd: str, send_newline: bool = True,
                         flush_before: bool = True):
        '''Send a command/data and return immediately. Identical to ConsoleBase.send()'''
        self.require_open()
        self.log(f'Sending command: "{cmd}"', force_log_file=None,
                 level=LogLevel.DEBUG)

        if flush_before:
            self.read_all()

        if send_newline:
            self.engine.send_line(cmd)
        else:
            self.engine.send(cmd)

        self.log(f'<<sent>>{cmd}<</sent>>',
                 force_echo=False, level=LogLevel.DEBUG)

    def send(self, cmd: str, send_newline: bool = True, flush_before: bool = True):
        '''Send a command/data. Identical to ConsoleBase.send_nonblocking()'''
        self.send_nonblocking(cmd=cmd, send_newline=send_newline, flush_before=flush_before)

    def send_control(self, char: str):
        self.require_open()
        self.engine.send_control(char)

    def check_alive(self, timeout=10.0):
        '''Return True if the console responds to <Enter>'''

        self.read_all(preserve_read_buffer=True)
        start_bytes = self.engine.reception_buffer_size
        self.send_nonblocking('', flush_before=False)
        alive = self.wait_for_bytes(timeout=timeout, start_bytes=start_bytes)

        if alive:
            self.log(f'Got response from: {self}')
        else:
            self.log(f'No response from: {self}')

        return alive

    def login(self, username, username_match,
              password=None, password_match=None, success_match=None):
        '''Attempt to login on the console using "username" and "password".'''
        matches = [username_match]
        if password_match:
            matches.append(password_match)
        if success_match:
            matches.append(success_match)

        fail_message = f'Failed to log in with login="{username}" and password="{password}"'
        (output, matched) = self.send_and_expect('', match=matches)
        if not matched:
            self.error(f'{fail_message}:{os.linesep}  Output: {output}',
                       ConsoleLoginFailedError)

        if matched == username_match:
            self.log(f'Login prompt detected, sending username "{username}"')
            matches.remove(username_match)
            (output, matched) = self.send_and_expect(cmd=username,
                                                     match=matches)

        if password_match and matched == password_match:
            if not password:
                self.error(f'{fail_message}: No password set, but password prompt detected',
                           ConsoleLoginFailedError)

            self.log('Password prompt detected, sending password')
            matches.remove(password_match)
            (output, matched) = self.send_and_expect(cmd=password,
                                                     match=matches)

        if matched:
            self.log('Prompt detected')
        elif not matched and success_match:
            self.error(f'{fail_message}: Failed to detect the prompt "{success_match}".'
                       'The prompt can be set in the target configuration with'
                       f' the "system.prompt_regex" attribute:{os.linesep}  Output: {output}',
                       ConsoleLoginFailedError)

        self.log('Login successful')

    def get_json_data(self, cmd):
        ''' Execute a command @cmd on target which generates JSON data.
        Parse this data, and return a dict of it.'''

        self.wait_for_quiet(quiet=1, sleep_time=0.5)
        received, matched = self.send_and_expect(cmd, match='{((.|\n)*)\n}')

        if not matched:
            raise ConsoleInvalidJSONReceivedError(
                f'No JSON found in command output: {received}')

        data = json.loads(matched)
        return data

    @property
    def support_file_copy(self):
        return False

    def copy_to_target(self, source, destination, timeout=30):
        raise ValueError(
            f'Console type {self} does not support copying to target')

    def copy_to_host(self, source, destination, timeout=30):
        raise ValueError(
            f'Console type {self} does not support copying from target')

    @property
    def requires_login(self):
        return self._requires_login

    def wait_for_prompt(self, timeout: int = None):
        '''Wait for a prompt, throws if no prompt before timeout'''

        prompt_regex = self.system.prompt_regex
        if not prompt_regex:
            raise ConsoleError('Trying to wait for prompt, but no prompt regex set. '
                               'Set a valid prompt regex for the console')

        self.log(f'Waiting for prompt "{prompt_regex}" for {timeout}s')
        match_result = self.engine.wait_for_match(match=prompt_regex, timeout=timeout)
        if not match_result.regex_matched:
            raise ConsoleError('No prompt detected.')
