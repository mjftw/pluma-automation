import os

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List

from pluma.utils import datetime_to_timestamp
from .consoleexceptions import ConsoleCannotOpenError


class ConsoleType(Enum):
    Process = 0
    FileDescriptor = 1


@dataclass(frozen=True)
class MatchResult:
    regex_matched: str
    text_matched: str
    text_received: str


class ConsoleEngine(ABC):
    def __init__(self, linesep: str = None, encoding: str = None,
                 raw_logfile: str = None):
        timestamp = datetime_to_timestamp(datetime.now())
        default_raw_logfile = os.path.join(
            '/tmp', 'pluma',
            f'{self.__class__.__name__}_raw_{timestamp}.log')

        self.linesep = linesep or '\n'
        self.encoding = encoding or 'ascii'
        self._console_type = None
        self.raw_logfile = raw_logfile or default_raw_logfile
        self._raw_logfile_fd = None

    @property
    def console_type(self):
        return self._console_type

    def open(self, console_cmd: str = None, console_fd=None):
        if (console_cmd is None and console_fd is None) or (
                console_cmd and console_fd):
            raise ValueError('Either "console_cmd" or "console_fd" must be provided.')

        if self.raw_logfile:
            os.makedirs(os.path.dirname(self.raw_logfile), exist_ok=True)
            self._raw_logfile_fd = open(self.raw_logfile, 'ab')

        try:
            if console_cmd:
                self._open_process(command=console_cmd)
                self._console_type = ConsoleType.Process
            else:
                self._open_fd(fd=console_fd)
                self._console_type = ConsoleType.FileDescriptor

            assert self.is_open
        except Exception:
            raise ConsoleCannotOpenError

    @abstractmethod
    def _open_process(self, command: str):
        '''Open a console by spawning a process'''

    @abstractmethod
    def _open_fd(self, fd):
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

        if self._raw_logfile_fd:
            self._raw_logfile_fd.close()
            self._raw_logfile_fd = None

    @abstractmethod
    def _close_fd(self):
        '''Close file descriptor based console'''

    @abstractmethod
    def _close_process(self):
        '''Close process based console'''

    @abstractmethod
    def send(self, data: str):
        '''Send data on the console.'''

    def send_line(self, data: str):
        '''Send data and a line break on the console.'''
        self.send(data+self.linesep)

    @abstractmethod
    def wait_for_match(self, match: List[str], timeout: int = None) -> MatchResult:
        '''Wait a maximum duration of 'timeout' for a matching regex'''

    @property
    @abstractmethod
    def reception_buffer_size(self) -> int:
        '''Size of the reception buffer for the console'''

    @property
    @abstractmethod
    def reception_buffer(self) -> str:
        '''Content of the reception buffer'''

    @abstractmethod
    def interact(self):
        '''Let the user interact with console'''

    def decode(self, text: bytes) -> str:
        '''Decode text using the engine's encoding'''
        if not text:
            return text

        if not isinstance(text, bytes):
            raise ValueError('"text" should be of type "bytes"')

        return text.decode(self.encoding, 'replace')

    def encode(self, text: str) -> bytes:
        '''Encode text using the engine's encoding'''
        if not text:
            return text

        if not isinstance(text, str):
            raise ValueError('"text" should be of type "str"')

        return text.encode(self.encoding)
