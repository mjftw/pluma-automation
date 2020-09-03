import pytest
from unittest.mock import MagicMock

from pluma.core import Board
from pluma.core.baseclasses import ConsoleBase

ssh_console = MagicMock(ConsoleBase)
serial_console = MagicMock(ConsoleBase)


def test_Board_should_support_no_console():
    Board(name='board')


def test_Board_should_support_empty_console_dict():
    Board(name='board', console={})


def test_Board_console_should_return_single_console_set():
    console1 = MagicMock(ConsoleBase)
    board = Board(name='board', console=console1)

    assert board.console is console1
    assert board.get_console() is console1


def test_Board_console_setter_should_set_current_console():
    board = Board(name='board')

    console2 = MagicMock(ConsoleBase)
    board.console = console2

    assert board.console is console2


def test_Board_console_should_return_the_first_console_by_default():
    console1 = MagicMock(ConsoleBase)
    console2 = MagicMock(ConsoleBase)
    board = Board(name='board', console={'def': console1, 'abc': console2})

    assert board.console is console1
    assert board.get_console() is console1


def test_Board_consoles_should_return_all_consoles():
    console1 = MagicMock(ConsoleBase)
    console1_name = 'abc'
    console2 = MagicMock(ConsoleBase)
    console2_name = 'def'
    consoles = {console1_name: console1, console2_name: console2}
    board = Board(name='board', console=consoles)

    assert board.consoles == consoles


def test_Board_get_console_should_return_the_proper_console_by_name():
    console1 = MagicMock(ConsoleBase)
    console1_name = 'abc'
    console2 = MagicMock(ConsoleBase)
    console2_name = 'def'
    board = Board(name='board', console={
                  console1_name: console1, console2_name: console2})

    assert board.get_console(console1_name) is console1
    assert board.get_console(console2_name) is console2


def test_Board_console_setter_should_keep_consoles_if_in_the_list():
    console1 = MagicMock(ConsoleBase)
    console1_name = 'abc'
    console2 = MagicMock(ConsoleBase)
    console2_name = 'def'
    consoles = {console1_name: console1, console2_name: console2}
    board = Board(name='board', console=consoles)

    assert board.console is console1
    board.console = console2

    assert board.console is console2
    assert board.consoles == consoles


def test_Board_console_setter_should_reset_consoles_if_not_in_the_list():
    console1 = MagicMock(ConsoleBase)
    console1_name = 'abc'
    board = Board(name='board', console={console1_name: console1})

    console2 = MagicMock(ConsoleBase)
    board.console = console2

    assert board.get_console(console1_name) is None


def test_Board_should_error_on_invalid_console_type():
    with pytest.raises(ValueError):
        Board(name='board', console=[])


def test_Board_consoles_setter_should_error_on_invalid_type():
    board = Board(name='board')
    with pytest.raises(ValueError):
        board.consoles = []
