import json
import pytest
from unittest.mock import MagicMock

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


def test_ConsoleBase_send_and_read_sends_data(basic_console):
    sent = 'abc'
    basic_console.send_and_read(cmd=sent, send_newline=False, timeout=0.1)
    assert basic_console.engine.sent == sent


def test_ConsoleBase_wait_for_prompt_should_error_if_not_detected(basic_console_class):
    prompt = 'user@host'
    console = basic_console_class(system=SystemContext(prompt_regex=prompt))

    console.engine.wait_for_match = MagicMock(return_value=MatchResult(None, None, ''))
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
