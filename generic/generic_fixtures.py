import pty
import os
from collections import namedtuple
from pytest import fixture
from unittest.mock import MagicMock
from farmcore import SoftPower, SerialConsole
from farmcore.mocks import ConsoleMock


class OsFile:
    def __init__(self, fd):
        self.fd = fd

    def read(self, n=None, encoding='ascii'):
        raw = os.read(self.fd, n or 10000)
        return raw.decode(encoding)

    def write(self, msg, encoding='ascii'):
        return os.write(self.fd, msg.encode(encoding))

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
        baud=115200 # Baud Doesn't really matter as virtual tty
    )

    SerialConsoleProxy = namedtuple('SerialConsoleProxy', ['proxy', 'console'])

    # === Return Fixture ===
    yield SerialConsoleProxy(OsFile(master), console)

    # === Teardown ===
    console.close()

    for fd in [master, slave]:
        try:
            os.close(fd)
        except OSError:
            pass
