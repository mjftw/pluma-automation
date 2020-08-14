import os
import pytest
import mock

from farmcore.baseclasses import ConsoleBase
from farmtest import CommandRunner


@mock.patch('farmcore.baseclasses.ConsoleBase')
def test_CommandRunner_query_return_code_should_call_send_and_read(mock_console):
    mock_console.send_and_read.return_value = ''
    CommandRunner.query_return_code(mock_console)
    mock_console.send_and_read.assert_called_once_with('echo retcode=$?')


@mock.patch('farmcore.baseclasses.ConsoleBase')
@pytest.mark.parametrize('console_output', ['abcdef', '', 'retcode=nothing'])
def test_CommandRunner_query_return_code_should_return_none_if_no_match(mock_console, console_output):
    mock_console.send_and_read.return_value = console_output
    assert CommandRunner.query_return_code(mock_console) == None


@mock.patch('farmcore.baseclasses.ConsoleBase')
@pytest.mark.parametrize('retcode', [0, 1, 127, -1, -127])
def test_CommandRunner_query_return_code_should_return_retcode(mock_console, retcode):
    mock_console.send_and_read.return_value = f'retcode={retcode}'
    assert CommandRunner.query_return_code(mock_console) == retcode


@mock.patch('farmcore.baseclasses.ConsoleBase')
def test_CommandRunner_query_return_code_should_work_with_dirty_output(mock_console):
    retcode = 123
    mock_console.send_and_read.return_value = f'abc\r\nabcretcode={retcode} abc\nabc'

    retcode_read = CommandRunner.query_return_code(mock_console)
    assert retcode == retcode_read
