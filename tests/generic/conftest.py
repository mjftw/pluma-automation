import pty
import os
from collections import namedtuple
from pytest import fixture
from unittest.mock import MagicMock

from utils import OsFile
from pluma import Board, SerialConsole, SoftPower
from pluma.core.baseclasses import ConsoleBase
from pluma.core.mocks import ConsoleMock


@fixture
def soft_power():
    mock_console = MagicMock(ConsoleMock())

    return SoftPower(
        console=mock_console,
        on_cmd='MOCK ON',
        off_cmd='MOCK OFF'
    )


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

    SerialConsoleProxy = namedtuple('SerialConsoleProxy', ['proxy', 'console'])

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
