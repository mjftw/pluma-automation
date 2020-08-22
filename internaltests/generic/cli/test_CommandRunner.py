import pytest

from farmtest import CommandRunner


def test_CommandRunner_query_return_code_should_call_send_and_read(mock_console):
    mock_console.send_and_read.return_value = ''
    CommandRunner.query_return_code(mock_console)
    mock_console.send_and_read.assert_called_once_with('echo retcode=$?')


@pytest.mark.parametrize('console_output', ['abcdef', '', 'retcode=nothing'])
def test_CommandRunner_query_return_code_should_return_none_if_no_match(mock_console, console_output):
    mock_console.send_and_read.return_value = console_output
    assert CommandRunner.query_return_code(mock_console) == None


@pytest.mark.parametrize('retcode', [0, 1, 127, -1, -127])
def test_CommandRunner_query_return_code_should_return_retcode(mock_console, retcode):
    mock_console.send_and_read.return_value = f'retcode={retcode}'
    assert CommandRunner.query_return_code(mock_console) == retcode


def test_CommandRunner_query_return_code_should_work_with_dirty_output(mock_console):
    retcode = 123
    mock_console.send_and_read.return_value = f'abc\r\nabcretcode={retcode} abc\nabc'

    retcode_read = CommandRunner.query_return_code(mock_console)
    assert retcode == retcode_read


def test_CommandRunner_output_matches_pattern_should_error_if_no_pattern():
    with pytest.raises(ValueError):
        CommandRunner.output_matches_pattern(None, 'abc')


@pytest.mark.parametrize('patterns,output', [('a', 'a'), ('b', 'abc'), (r'\d', 'abc123'), ('def', 'abc\ndef')])
def test_CommandRunner_output_matches_pattern_should_match_pattern(patterns, output):
    assert CommandRunner.output_matches_pattern(patterns, output) == True


@pytest.mark.parametrize('patterns,output', [(['a', 'b'], 'a'), (['a', 'b'], 'b')])
def test_CommandRunner_output_matches_pattern_should_match_pattern_list(patterns, output):
    assert CommandRunner.output_matches_pattern(patterns, output) == True


@pytest.mark.parametrize('patterns,output', [('a', 'b'), (r'\d', 'abcd')])
def test_CommandRunner_output_matches_pattern_should_not_match_pattern(patterns, output):
    assert CommandRunner.output_matches_pattern(patterns, output) == False
