import pytest

from pluma.test import CommandRunner, TaskFailed


def test_CommandRunner_query_return_code_should_call_send_and_read(mock_console):
    mock_console.send_and_read.return_value = ''
    CommandRunner.query_return_code(mock_console)
    mock_console.send_and_read.assert_called_once_with('echo retcode=$?')


@pytest.mark.parametrize('console_output', ['abcdef', '', 'retcode=nothing'])
def test_CommandRunner_query_return_code_should_return_none_if_no_match(mock_console,
                                                                        console_output):
    mock_console.send_and_read.return_value = console_output
    assert CommandRunner.query_return_code(mock_console) is None


@pytest.mark.parametrize('retcode', [0, 1, 127, -1, -127])
def test_CommandRunner_query_return_code_should_return_retcode(mock_console, retcode):
    mock_console.send_and_read.return_value = f'retcode={retcode}'
    assert CommandRunner.query_return_code(mock_console) == retcode


def test_CommandRunner_query_return_code_should_work_with_dirty_output(mock_console):
    retcode = 123
    mock_console.send_and_read.return_value = f'abc\r\nabcretcode={retcode} abc\nabc'

    retcode_read = CommandRunner.query_return_code(mock_console)
    assert retcode == retcode_read


@pytest.mark.parametrize('patterns, output, expected',
                         [(None, 'a', False), (['a', 'b'], 'a', True),
                          (['a', 'b'], 'b', True), (['a', 'b'], 'ab', True)])
def test_CommandRunner_output_matches_any_pattern(patterns, output, expected):
    assert CommandRunner.output_matches_any_pattern(patterns, output) is expected


@pytest.mark.parametrize('patterns, output, expected',
                         [(None, 'a', True), (['a', 'b'], 'a', False),
                          (['a', 'b'], 'b', False), (['a', 'b'], 'ab', True)])
def test_CommandRunner_output_matches_all_patterns(patterns, output, expected):
    assert CommandRunner.output_matches_all_patterns(patterns, output) is expected


@pytest.mark.parametrize('patterns,output', [('a', 'a'), ('b', 'abc'), (r'\d', 'abc123'),
                                             ('def', 'abc\ndef')])
def test_CommandRunner_output_matches_methods_should_match_regex(patterns, output):
    assert CommandRunner.output_matches_any_pattern(patterns, output) is True
    assert CommandRunner.output_matches_all_patterns(patterns, output) is True


@pytest.mark.parametrize('patterns,output', [(['a', 'b'], 'abc')])
def test_CommandRunner_output_matches_methods_should_match_list(patterns, output):
    assert CommandRunner.output_matches_any_pattern(patterns, output) is True
    assert CommandRunner.output_matches_all_patterns(patterns, output) is True


@pytest.mark.parametrize('match_regex, error_regex, output',
                         [('valid', None, 'valid'),
                          ('valid', 'not_valid', 'valid'),
                          (None, 'not_valid', 'valid')])
def test_CommandRunner_check_output_should_succeed(match_regex, error_regex, output):

    CommandRunner.check_output(test_name='test', command='cmd', output=output,
                               match_regex=match_regex, error_regex=error_regex)


@pytest.mark.parametrize('match_regex, error_regex, output',
                         [('valid', None, 'other'),
                          ('valid', 'not_valid', 'not_valid'),
                          (None, 'not_valid', 'not_valid')])
def test_CommandRunner_check_output_should_error(match_regex, error_regex, output):
    with pytest.raises(TaskFailed):
        CommandRunner.check_output(test_name='test', command='cmd', output=output,
                                   match_regex=match_regex, error_regex=error_regex)
