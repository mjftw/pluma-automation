import json
import pytest
import time
from unittest.mock import MagicMock

from utils import nonblocking

from pluma.core.baseclasses import (ConsoleError, ConsoleInvalidJSONReceivedError,
                                    MatchResult)
from pluma.core.dataclasses import SystemContext


def test_ConsoleBase_send_sends_data(basic_console):
    sent = 'abc'
    basic_console.send(cmd=sent, send_newline=False)
    assert basic_console.engine.sent == sent


def test_ConsoleBase_send_with_newline_sends_newline(basic_console):
    sent = 'abc'
    basic_console.send(cmd=sent, send_newline=True)
    assert basic_console.engine.sent == sent+basic_console.engine.linesep


def test_ConsoleBase_send_should_discard_reception_with_read_all(
        basic_console):
    basic_console.engine.read_all = MagicMock()

    basic_console.send(cmd='abc', send_newline=True)

    basic_console.engine.read_all.assert_called_once_with(preserve_read_buffer=False)


@pytest.mark.parametrize('sleep_time', [0.2, 1])
def test_ConsoleBase_wait_for_quiet_should_wait_at_least_sleep_time(basic_console,
                                                                    sleep_time):
    start = time.time()
    success = basic_console.wait_for_quiet(quiet=0, sleep_time=sleep_time, timeout=2)
    elapsed = time.time() - start

    assert success is True
    assert 0.8*sleep_time < elapsed < 1.2*sleep_time


@pytest.mark.parametrize('timeout', [0.2, 1])
def test_ConsoleBase_wait_for_quiet_should_wait_at_most_timeout(basic_console, timeout):
    start = time.time()
    success = basic_console.wait_for_quiet(quiet=timeout*2, timeout=timeout)
    elapsed = time.time() - start

    assert success is False
    assert 0.8*timeout < elapsed < 1.2*timeout


@pytest.mark.parametrize('quiet_time, non_quiet_time', [(0.2, 0.5), (0.5, 1)])
def test_ConsoleBase_wait_for_quiet_should_return_when_quiet(basic_console,
                                                             quiet_time, non_quiet_time):
    start = time.time()
    async_result = nonblocking(basic_console.wait_for_quiet,
                               quiet=quiet_time, timeout=5)

    data_end = start + non_quiet_time
    while(time.time() < data_end):
        basic_console.engine.received += 'abc'
        time.sleep(0.025)

    success = async_result.get()
    elapsed = time.time() - start

    assert success is True
    total_time = non_quiet_time+quiet_time
    assert 0.8*total_time < elapsed < 1.2*total_time


def test_ConsoleBase_send_and_read_sends_data(basic_console):
    sent = 'abc'
    basic_console.send_and_read(cmd=sent, send_newline=False, timeout=0.1)
    assert basic_console.engine.sent == sent


def test_ConsoleBase_send_and_expect_returns_received_and_none_when_no_match_available(
        basic_console):
    match_result = MatchResult(regex_matched=None,
                               text_matched=None,
                               text_received='abc\ndef')
    basic_console.engine.wait_for_match = MagicMock(return_value=match_result)

    async_result = nonblocking(basic_console.send_and_expect,
                               cmd='', match='anything', timeout=0.2)

    received, matched = async_result.get()
    assert received == match_result.text_received
    assert matched is None


def test_ConsoleBase_send_and_expect_returns_received_and_matched_text_when_match_available(
        basic_console):
    match_result = MatchResult(regex_matched='ab*c',
                               text_matched='abc',
                               text_received='abc\ndef')
    basic_console.engine.wait_for_match = MagicMock(return_value=match_result)

    async_result = nonblocking(basic_console.send_and_expect,
                               cmd='', match='anything', timeout=0.2)

    received, matched = async_result.get()
    assert received == match_result.text_received
    assert matched == match_result.text_matched


def test_ConsoleBase_send_and_expect_match_multiline_reception(
        basic_console):
    match_result = MatchResult(regex_matched='de*f',
                               text_matched='abc',
                               text_received='abc\ndef')
    basic_console.engine.wait_for_match = MagicMock(return_value=match_result)

    async_result = nonblocking(basic_console.send_and_expect,
                               cmd='', match='anything', timeout=0.2)

    received, matched = async_result.get()
    assert received == match_result.text_received
    assert matched == match_result.text_matched


def test_ConsoleBase_wait_for_prompt_should_error_if_not_detected(basic_console_class):
    prompt = 'user@host'
    console = basic_console_class(system=SystemContext(prompt_regex=prompt))

    console.engine.wait_for_match = MagicMock(
        return_value=MatchResult(None, None, ''))
    with pytest.raises(ConsoleError):
        console.wait_for_prompt(timeout=0.1)


def test_ConsoleBase_wait_for_prompt_should_succeed_if_matched(basic_console_class):
    prompt = 'user@host'
    console = basic_console_class(system=SystemContext(prompt_regex=prompt))

    console.engine.wait_for_match = MagicMock(return_value=MatchResult(prompt, prompt, prompt))
    console.wait_for_prompt(timeout=0.1)


def test_ConsoleBase_wait_for_prompt_should_call_wait_for_match(basic_console_class):
    prompt = 'user@host'
    console = basic_console_class(system=SystemContext(prompt_regex=prompt))
    timeout = 0.13

    console.engine.wait_for_match = MagicMock(return_value=MatchResult(prompt, prompt, prompt))
    console.wait_for_prompt(timeout=timeout)
    console.engine.wait_for_match.assert_called_with(match=prompt, timeout=timeout)


def test_ConsoleBase_get_json_data_should_error_if_not_json(basic_console):
    basic_console.send_and_expect = MagicMock(return_value=('abc\ndef', None))

    with pytest.raises(ConsoleInvalidJSONReceivedError):
        basic_console.get_json_data(cmd='command')

    basic_console.send_and_expect.assert_called_once()


def test_ConsoleBase_get_json_data_return_object(basic_console):
    json_data = '{"abc":"def", "other":"value"}'
    received = f'there will be json {json_data} the end.'
    basic_console.send_and_expect = MagicMock(return_value=(received, json_data))

    json_result = basic_console.get_json_data(cmd='command')

    basic_console.send_and_expect.assert_called_once()
    assert json_result == json.loads(json_data)


def test_ConsoleBase_get_json_data_should_match_json(basic_console):
    json_data = '{"abc":"def", "other":"value"}'

    result = MatchResult('some_regex', json_data, f'there will be json {json_data} the end.')
    basic_console.engine.wait_for_match = MagicMock(return_value=result)
    json_result = basic_console.get_json_data(cmd='command')
    assert json_result == json.loads(json_data)


def test_ConsoleBase_send_control_calls_engines_send_control(basic_console):
    basic_console.engine.send_control = MagicMock()

    basic_console.send_control('C')
    basic_console.engine.send_control.assert_called_with('C')


def test_ConsoleBase_should_call_open_for_wait_for_match(basic_console):
    basic_console.close()
    assert not basic_console.is_open

    basic_console.open = MagicMock(side_effect=basic_console.open)

    basic_console.wait_for_match(['foo'])
    basic_console.open.assert_called()


def test_ConsoleBase_should_call_open_for_read_all(basic_console):
    basic_console.close()
    assert not basic_console.is_open

    basic_console.open = MagicMock(side_effect=basic_console.open)

    basic_console.read_all()
    basic_console.open.assert_called()


def test_ConsoleBase_should_call_open_for_wait_for_bytes(basic_console):
    basic_console.close()
    assert not basic_console.is_open

    basic_console.open = MagicMock(side_effect=basic_console.open)

    basic_console.wait_for_bytes(0.1)
    basic_console.open.assert_called()


def test_ConsoleBase_should_call_open_for_wait_for_quiet(basic_console):
    basic_console.close()
    assert not basic_console.is_open

    basic_console.open = MagicMock(side_effect=basic_console.open)

    basic_console.wait_for_quiet(0.1)
    basic_console.open.assert_called()


def test_ConsoleBase_should_call_open_for_send_and_read(basic_console):
    basic_console.close()
    assert not basic_console.is_open

    basic_console.open = MagicMock(side_effect=basic_console.open)

    basic_console.send_and_read('foo')
    basic_console.open.assert_called()


def test_ConsoleBase_should_call_open_for_send_and_expect(basic_console):
    basic_console.close()
    assert not basic_console.is_open

    basic_console.open = MagicMock(side_effect=basic_console.open)

    basic_console.send_and_expect('foo', ['bar'])
    basic_console.open.assert_called()


def test_ConsoleBase_should_call_open_for_send_nonblocking(basic_console):
    basic_console.close()
    assert not basic_console.is_open

    basic_console.open = MagicMock(side_effect=basic_console.open)

    basic_console.send_nonblocking('foo')
    basic_console.open.assert_called()


def test_ConsoleBase_should_call_open_for_send(basic_console):
    basic_console.close()
    assert not basic_console.is_open

    basic_console.open = MagicMock(side_effect=basic_console.open)

    basic_console.send('foo')
    basic_console.open.assert_called()


def test_ConsoleBase_should_call_open_for_send_control(basic_console):
    basic_console.close()
    assert not basic_console.is_open

    basic_console.open = MagicMock(side_effect=basic_console.open)

    basic_console.send_control('C')
    basic_console.open.assert_called()