from pluma.test.testbase import NoopTest
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


def test_Session_setup_calls_session_setup(mock_board):
    mock_board.power = Mock(PowerBase)
    test1 = NoopTest()
    test1.session_setup = Mock(NoopTest.session_setup)
    test2 = NoopTest()
    test2.session_setup = Mock(NoopTest.session_setup)

    session = Session(mock_board, tests=[test1, test2])
    session.setup()

    for test in session.tests:
        test.session_setup.assert_called_once()


def test_Session_teardown_calls_session_teardown(mock_board):
    mock_board.power = Mock(PowerBase)
    test1 = NoopTest()
    test1.session_teardown = Mock(NoopTest.session_setup)
    test2 = NoopTest()
    test2.session_teardown = Mock(NoopTest.session_setup)

    session = Session(mock_board, tests=[test1, test2])
    session.teardown()

    for test in session.tests:
        test.session_teardown.assert_called_once()
