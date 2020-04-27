from pytest import fixture
from unittest.mock import MagicMock
from farmcore import SoftPower
from farmcore.mocks import ConsoleMock


@fixture
def soft_power():
    mock_console = MagicMock(ConsoleMock())

    return SoftPower(
        console=mock_console,
        on_cmd='MOCK ON',
        off_cmd='MOCK OFF'
    )
