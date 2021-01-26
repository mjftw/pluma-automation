from unittest.mock import Mock

from pluma.test import Session
from pluma.core.baseclasses import PowerBase


def test_Session_setup_reboots_device(mock_board):
    mock_board.power = Mock(PowerBase)
    session = Session(mock_board)
    session.setup()

    mock_board.power.reboot.assert_called_once()


def test_Session_teardown_powers_off_device(mock_board):
    mock_board.power = Mock(PowerBase)
    session = Session(mock_board)
    session.teardown()

    mock_board.power.off.assert_called_once()
