import pexpect
import pexpect.fdpexpect

from typing import List, IO, Optional, Union

from pluma.core.baseclasses import ConsoleEngine, MatchResult
from .logging import Logger

log = Logger()


class PexpectEngine(ConsoleEngine):
    def __init__(self, linesep: Optional[str] = None, encoding: Optional[str] = None,
                 raw_logfile: Optional[str] = None):
        super().__init__(linesep=linesep, encoding=encoding,
                         raw_logfile=raw_logfile)
        self._pex = None

    def _open_process(self, command: str, log_file: Optional[IO] = None):
        self._pex = pexpect.spawn(command, timeout=0.01, logfile=log_file)

    def _open_fd(self, fd: int, log_file: Optional[IO] = None):
        self._pex = pexpect.fdpexpect.fdspawn(fd=fd, timeout=0.5)
        # Use the logfile_read to avoid seeing commands sent twice for TTYs.
        self._pex.logfile_read = log_file

    @property
    def is_open(self):
        return bool(self._pex and self._pex.isalive())

    def _close_fd(self):
        self._pex.close()
        self._pex = None

    def _close_process(self):
        self._pex.close()
        self._pex = None

    def send(self, data: str):
        assert self.is_open
        self._pex.send(data)

    def send_control(self, char: str):
        assert self.is_open
        if len(char) > 1:
            raise ValueError('Only a single character can be sent as control code, '
                             f'but got {char}')

        code_ascii_value = ord(char.upper()) - ord('A') + 1
        if code_ascii_value not in range(1, 27):
            raise AttributeError('Control character must be A-Z')

        code = bytes([code_ascii_value])
        self._pex.send(code)

    def _read_from_console(self) -> str:
        received = ''
        try:
            while 1:
                received += self.decode(
                    self._pex.read_nonblocking(1, 0.01))
        except pexpect.TIMEOUT:
            pass
        except pexpect.EOF:
            pass

        return received

    def wait_for_match(self, match: Union[str, List[str]],
                       timeout: Optional[float] = None) -> MatchResult:
        '''Wait a maximum duration of 'timeout' for a matching regex'''
        assert self.is_open

        timeout = timeout or self._pex.timeout

        if isinstance(match, str):
            match = [match]

        log.debug(f'Waiting up to {timeout}s for patterns: {match}...')

        matched_regex = None
        try:
            index = self._pex.expect(match, timeout)
            matched_regex = match[index]
        except pexpect.EOF:
            pass
        except pexpect.TIMEOUT:
            pass

        if matched_regex:
            log.debug(f'Matched {matched_regex}')
        else:
            log.debug('No match found before timeout or EOF')

        # Pexpect exposes received via '.before'
        matched_text: Optional[bytes]
        received: bytes = self._pex.before if self._pex.before is not None else bytes()
        if matched_regex:
            matched_text = self._pex.after
            received += matched_text
        else:
            matched_regex = None
            matched_text = None

        text_matched = self.decode(matched_text) if matched_text else None
        text_received = self.decode(received)

        return MatchResult(regex_matched=matched_regex, text_matched=text_matched,
                           text_received=text_received)

    def interact(self):
        assert self.is_open
        self._pex.interact()
