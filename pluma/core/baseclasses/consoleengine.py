import os

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, IO, Optional, Union

from pluma.utils import datetime_to_timestamp
from .consoleexceptions import ConsoleCannotOpenError
from .logging import Logger

log = Logger()


class ConsoleType(Enum):
    Process = 0
    FileDescriptor = 1


@dataclass(frozen=True)
class MatchResult:
    regex_matched: Optional[str]
    text_matched: Optional[str]
    text_received: str


class ConsoleEngine(ABC):
    def __init__(self, linesep: Optional[str] = None, encoding: Optional[str] = None,
                 raw_logfile: Optional[str] = None):
        timestamp = datetime_to_timestamp(datetime.now())
        default_raw_logfile = os.path.join(
            '/tmp', 'pluma',
            f'{self.__class__.__name__}_raw_{timestamp}.log')

        self.linesep = linesep or '\n'
        self.encoding = encoding or 'ascii'
        self.raw_logfile = raw_logfile or default_raw_logfile
        self._raw_logfile_io = None
        self._console_type = None
        self._reception_buffer = ''

    @property
    def console_type(self):
        return self._console_type

    def open(self, console_cmd: Optional[str] = None, console_fd: Optional[int] = None):
        if (console_cmd is None and console_fd is None) or (
                console_cmd is not None and console_fd is not None):
            raise ValueError('Either "console_cmd" or "console_fd" must be provided.')

        if self.raw_logfile:
            dirpath = os.path.dirname(self.raw_logfile)
            if dirpath:
                os.makedirs(dirpath, exist_ok=True)

            self._raw_logfile_io = open(self.raw_logfile, 'wb')

        try:
            if console_cmd is not None:
                self._open_process(command=console_cmd, log_file=self._raw_logfile_io)
                self._console_type = ConsoleType.Process
            elif console_fd is not None:
                self._open_fd(fd=console_fd, log_file=self._raw_logfile_io)
                self._console_type = ConsoleType.FileDescriptor
            else:
                raise Exception('Unreachable branch')

            assert self.is_open
        except Exception:
            raise ConsoleCannotOpenError

    @abstractmethod
    def _open_process(self, command: str, log_file: Optional[IO] = None):
        '''Open a console by spawning a process'''

    @abstractmethod
    def _open_fd(self, fd: int, log_file: Optional[IO] = None):
        '''Open a specific file descriptor as the console'''

    @property
    @abstractmethod
    def is_open(self):
        '''Return whether the console is open or not'''

    def close(self):
        '''Close the console.'''
        if not self.is_open:
            return

        if self.console_type is ConsoleType.Process:
            self._close_process()
        elif self.console_type is ConsoleType.FileDescriptor:
            self._close_fd()
        else:
            raise Exception(f'Unknown console_type {self.console_type}')

        if self._raw_logfile_io:
            self._raw_logfile_io.close()
            self._raw_logfile_io = None

    @abstractmethod
    def _close_fd(self):
        '''Close file descriptor based console'''

    @abstractmethod
    def _close_process(self):
        '''Close process based console'''

    @abstractmethod
    def send(self, data: str):
        '''Send data on the console.'''

    @abstractmethod
    def send_control(self, char: str):
        '''Send control character on the console.'''

    def send_line(self, data: str):
        '''Send data and a line break on the console.'''
        self.send(data+self.linesep)

    def read_all(self, preserve_read_buffer: bool = False):
        '''Read and return all data available on the console'''
        assert self.is_open

        self._reception_buffer += self._read_from_console()
        received = self._reception_buffer

        if not preserve_read_buffer:
            if self._reception_buffer.strip():
                log.debug(f'<<flushed>>{self._reception_buffer}<</flushed>>')
            self._reception_buffer = ''

        return received

    @abstractmethod
    def _read_from_console(self) -> str:
        '''Read and return all data available on the console'''

    @abstractmethod
    def wait_for_match(self, match: Union[str, List[str]],
                       timeout: Optional[float] = None) -> MatchResult:
        '''Wait a maximum duration of 'timeout' for a matching regex'''

    @property
    def reception_buffer_size(self) -> int:
        '''Size of the reception buffer for the console'''
        return len(self._reception_buffer)

    @property
    def reception_buffer(self) -> str:
        '''Content of the reception buffer'''
        return self._reception_buffer

    @abstractmethod
    def interact(self):
        '''Let the user interact with console'''

    def decode(self, text: bytes) -> str:
        '''Decode text using the engine's encoding'''
        if not isinstance(text, bytes):
            raise TypeError('"text" should be of type "bytes"')

        return text.decode(self.encoding, 'replace')

    def encode(self, text: str) -> bytes:
        '''Encode text using the engine's encoding'''
        if not isinstance(text, str):
            raise TypeError('"text" should be of type "str"')

        return text.encode(self.encoding)
