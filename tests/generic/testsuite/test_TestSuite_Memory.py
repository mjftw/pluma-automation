import pytest
from unittest.mock import MagicMock
from pluma.test import TaskFailed
from pluma.plugins.testsuite import MemorySize


def test_MemorySize_should_error_if_no_argument(mock_board):
    with pytest.raises(ValueError):
        MemorySize(mock_board)


@pytest.mark.parametrize('total, available', [(1, None), (None, 1), (1, 1)])
def test_MemorySize_should_accept_argument_combination(mock_board, total, available):
    MemorySize(mock_board, total_mb=total, available_mb=available)


def test_MemorySize_should_cat_proc_meminfo(mock_board, basic_console):
    mock_board.console = basic_console
    action = MemorySize(mock_board, total_mb=1024, available_mb=512)

    with pytest.raises(TaskFailed):
        action.test_body()

    assert mock_board.console.engine.sent == 'cat /proc/meminfo\n'


@pytest.mark.parametrize('total, available, total_actual, available_actual',
                         [(123, None, 123, 123), (None, 123, 123, 124)])
def test_MemorySize_should_pass_on_correct_values(mock_board, basic_console,
                                                  total, total_actual,
                                                  available, available_actual):

    mock_board.console = basic_console
    action = MemorySize(mock_board, total_mb=total, available_mb=available)

    mock_board.console.send_and_read = MagicMock()
    received = (f'MemTotal:  {total_actual*1024} KB\n'
                f'MemFree:  {available_actual*1024} KB\n')
    mock_board.console.send_and_read.return_value = received

    action.test_body()


@pytest.mark.parametrize('total, available, total_actual, available_actual',
                         [(1024, None, 512, 123), (1024, None, None, 123),
                          (None, 512, 1024, 123), (None, 512, 512, None)])
def test_MemorySize_should_error_on_incorrect_values(mock_board, basic_console,
                                                     total, total_actual,
                                                     available, available_actual):
    mock_board.console = basic_console
    action = MemorySize(mock_board, total_mb=total, available_mb=available)

    mock_board.console.send_and_read = MagicMock()
    received = (f'MemTotal:  {total_actual*1024 if total_actual else total_actual} KB\n'
                f'MemFree:  {available_actual*1024 if available_actual else available_actual} KB\n')
    mock_board.console.send_and_read.return_value = received

    with pytest.raises(TaskFailed):
        action.test_body()
