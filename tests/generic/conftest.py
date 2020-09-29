from traceback import format_exc
from typing import Iterable
import pty
import os
import sys
import time
from pytest import fixture
from unittest.mock import MagicMock, patch
import traceback
import tempfile
import textwrap
import shutil

from utils import OsFile
from pluma import Board, SerialConsole, SoftPower, SSHConsole
from pluma.core.baseclasses import ConsoleBase
from pluma.core.dataclasses import SystemContext, Credentials
from pluma.core.mocks import ConsoleMock
from pluma import __main__

@fixture
def soft_power():
    mock_console = MagicMock(ConsoleMock())

    return SoftPower(
        console=mock_console,
        on_cmd='MOCK ON',
        off_cmd='MOCK OFF'
    )


class SerialConsoleProxy:
    def __init__(self, proxy, console: ConsoleBase):
        self.proxy = proxy
        self.console = console

    def fake_reception(self, message: str):
        time.sleep(0.1)
        self.proxy.write(message)

    def read_serial_output(self):
        # Give time for the data written to propagate
        return self.proxy.read(timeout=0.2)


@fixture
def serial_console_proxy():
    # === Setup ===
    master, slave = pty.openpty()

    slave_device = os.ttyname(slave)

    console = SerialConsole(
        port=slave_device,
        baud=115200,  # Baud Doesn't really matter as virtual tty,
        encoding='utf-8'
    )

    proxy = OsFile(master, console.encoding)

    # Clear master file just in case
    proxy.read(timeout=0)

    # === Return Fixture ===
    yield SerialConsoleProxy(proxy, console)

    # === Teardown ===
    console.close()

    for fd in [master, slave]:
        try:
            os.close(fd)
        except OSError:
            pass


@fixture
def minimal_ssh_console():
    return SSHConsole(target="localhost", system=SystemContext(Credentials("root")))


@fixture
def mock_console():
    return MagicMock(ConsoleBase)


@fixture
def mock_board(mock_console):
    mock_board = MagicMock(Board)
    mock_board.console = mock_console

    return mock_board


@fixture
def target_config():
    return {}


@fixture
def ssh_config():
    return {
        'target': '123',
        'login': 'abc'
    }


@fixture
def serial_config():
    return {
        'port': 'abc',
        'baud': 123,
    }


@fixture
def pluma_cli(capsys):
    '''Get a function that can be used to call the Pluma CLI with given args and catches exits'''
    def pluma_cli(args: Iterable[str] = []):
        assert isinstance(args, Iterable)

        # Override actual CLI arguments with supplied
        with patch.object(sys, 'argv', [sys.argv[0], *args]):
            try:
                __main__.main()
            except SystemExit as e:
                if e.code != 0:
                    readouterr = capsys.readouterr()
                    e_msg = f'Pluma CLI exited with code {e.code}'
                    print(
                        f'{e_msg}',
                        f'{os.linesep}stdout: {readouterr.out}' if readouterr.out else '',
                        f'{os.linesep}stderr: {readouterr.err}' if readouterr.err else '',
                    )
                    traceback.print_exc()

                    raise RuntimeError(e_msg)

    return pluma_cli


@fixture
def temp_file():
    '''Return a function that creates temporary files with content and returns their names.'''
    tempdir = tempfile.mkdtemp()

    def temp_file(content: str = None, dedent: bool = True) -> str:
        '''Create a temporary file with the given content and return its name.
        Set dedent to allow natural indentation in multiline strings.
        '''
        _, filename = tempfile.mkstemp(dir=tempdir)

        if content:
            if dedent:
                # Remove leading newlines and global indent
                content = textwrap.dedent(content)
                content = content.lstrip(os.linesep)

            with open(filename, 'w') as f:
                f.write(content)

        return filename

    # Return the function used to create temporary files
    yield temp_file

    # Cleanup
    shutil.rmtree(tempdir)

