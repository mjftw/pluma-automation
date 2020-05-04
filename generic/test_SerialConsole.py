import os
import time
import pytest
from farmcore.exceptions import ConsoleLoginFailedError

from generic_fixtures import serial_console_proxy
from utils import nonblocking


def test_SerialConsole_send_sends_data(serial_console_proxy):
    serial_console_proxy.console.send('Foo')

    written = serial_console_proxy.proxy.read()

    assert written


def test_SerialConsole_send_sends_correct_data(serial_console_proxy):
    msg = 'Foo'
    serial_console_proxy.console.send(msg)

    written = serial_console_proxy.proxy.read()

    assert written == '{}{}'.format(msg, serial_console_proxy.console.linesep)


def test_SerialConsole_send_doesnt_send_newline_when_send_newline_arg_false(serial_console_proxy):
    msg = 'Foo'
    serial_console_proxy.console.send(msg, send_newline=False)

    written = serial_console_proxy.proxy.read()

    assert written == msg


def test_SerialConsole_send_returns_tuple(serial_console_proxy):
    returned = serial_console_proxy.console.send()

    assert isinstance(returned, tuple)


def test_SerialConsole_send_returns_tuple_length_2(serial_console_proxy):
    returned = serial_console_proxy.console.send()

    assert len(returned) == 2

def test_SerialConsole_send_returns_data_when_recieve_arg_true(serial_console_proxy):
    msg = 'Bar'

    async_result = nonblocking(serial_console_proxy.console.send,
        receive=True)

    # Wait short time for function to start
    time.sleep(0.1)

    serial_console_proxy.proxy.write(msg)

    received, __ = async_result.get()
    assert received == msg


def test_SerialConsole_send_returns_matched_when_match_available(serial_console_proxy):
    before_match, to_match = 'Foo', 'Bar'
    msg = before_match + to_match

    async_result = nonblocking(serial_console_proxy.console.send,
        match=to_match)

    # Wait short time for function to start
    time.sleep(0.1)

    serial_console_proxy.proxy.write(msg)

    __, matched = async_result.get()
    assert matched == to_match


def test_SerialConsole_send_returns_received_when_match_available(serial_console_proxy):
    before_match, to_match = 'Foo', 'Bar'
    msg = before_match + to_match

    async_result = nonblocking(serial_console_proxy.console.send,
        match=to_match)

    # Wait short time for function to start
    time.sleep(0.1)

    serial_console_proxy.proxy.write(msg)

    received, __ = async_result.get()
    assert received == before_match


def test_SerialConsole_send_returns_received_false_when_no_match_available(serial_console_proxy):
    msg = 'FooBar'
    wont_match = 'Baz'

    async_result = nonblocking(serial_console_proxy.console.send,
        match=wont_match)

    # Wait short time for function to start
    time.sleep(0.1)

    serial_console_proxy.proxy.write(msg)

    __, matched = async_result.get()
    assert matched is False


def test_SerialConsole_send_returns_received_when_no_match_available(serial_console_proxy):
    msg = 'FooBar'
    wont_match = 'Baz'

    async_result = nonblocking(serial_console_proxy.console.send,
        match=wont_match)

    # Wait short time for function to start
    time.sleep(0.1)

    serial_console_proxy.proxy.write(msg)

    received, __ = async_result.get()
    assert received == msg


def test_SerialConsole_send_matches_regex(serial_console_proxy):
    msg = 'Hello World! 123FooBarBaz'
    regex = '[0-3]+Foo'
    expected_match='123Foo'

    async_result = nonblocking(serial_console_proxy.console.send,
        match=regex)

    # Wait short time for function to start
    time.sleep(0.1)

    serial_console_proxy.proxy.write(msg)

    __, matched = async_result.get()
    assert matched == expected_match


def test_SerialConsole_check_alive_returns_true_when_target_responds(serial_console_proxy):
        async_result = nonblocking(
            serial_console_proxy.console.check_alive)

        # Wait short time for function to start
        time.sleep(0.1)

        # Send console a newline char
        serial_console_proxy.proxy.write(serial_console_proxy.console.linesep)

        assert async_result.get() is True


def test_SerialConsole_check_alive_returns_true_when_target_not_responds(serial_console_proxy):
        async_result = nonblocking(
            serial_console_proxy.console.check_alive,
            timeout=1)

        # Send no response to console

        assert async_result.get() is False


def test_SerialConsole_login_finds_user_match_sends_correct_username(serial_console_proxy):
        user_match = 'Enter username: '
        username = 'Foo'

        async_result = nonblocking(
            serial_console_proxy.console.login,
            username_match=user_match,
            username=username)

        # Wait short time for function to start
        time.sleep(0.1)

        for i in range(0, 10):
            serial_console_proxy.proxy.write(
                f'Nonsense non matching line {i}...')
            time.sleep(0.01)

        serial_console_proxy.proxy.write(user_match)

        # Wait for response
        time.sleep(0.01)

        received = serial_console_proxy.proxy.read()
        expected = f'{username}{serial_console_proxy.console.linesep}'

        assert received == expected


def test_SerialConsole_login_success_with_no_password(serial_console_proxy):
        user_match = 'Enter username: '
        username = 'Foo'

        async_result = nonblocking(
            serial_console_proxy.console.login,
            username_match=user_match,
            username=username)

        # Wait short time for function to start
        time.sleep(0.1)

        for i in range(0, 10):
            serial_console_proxy.proxy.write(
                f'Nonsense non matching line {i}...')
            time.sleep(0.01)

        serial_console_proxy.proxy.write(user_match)

        # Wait for response
        time.sleep(0.01)

        received = serial_console_proxy.proxy.read()
        expected = f'{username}{serial_console_proxy.console.linesep}'

        assert received == expected

        # Wait for console.login() to finish
        async_result.get()

        # If we've gotten to here without error then success
        assert True


def test_SerialConsole_login_finds_pass_match_sends_correct_pass(serial_console_proxy):
        user_match = 'Enter username: '
        pass_match = 'Enter password: '
        username = 'Foo'
        password = 'Bar'

        async_result = nonblocking(
            serial_console_proxy.console.login,
            username_match=user_match,
            password_match=pass_match,
            username=username,
            password=password)

        # Wait short time for function to start
        time.sleep(0.1)

        for i in range(0, 10):
            serial_console_proxy.proxy.write(
                f'Nonsense non matching line {i}...')
            time.sleep(0.01)

        serial_console_proxy.proxy.write(user_match)

        # Wait for response
        time.sleep(0.01)

        received = serial_console_proxy.proxy.read()
        expected = f'{username}{serial_console_proxy.console.linesep}'

        assert received == expected

        serial_console_proxy.proxy.write(pass_match)

        # Wait for response
        time.sleep(0.01)

        received = serial_console_proxy.proxy.read()
        expected = f'{password}{serial_console_proxy.console.linesep}'

        assert received == expected


def test_SerialConsole_login_no_exception_on_success_no_success_match(serial_console_proxy):
        user_match = 'Enter username: '
        pass_match = 'Enter password: '
        username = 'Foo'
        password = 'Bar'

        async_result = nonblocking(
            serial_console_proxy.console.login,
            username_match=user_match,
            password_match=pass_match,
            username=username,
            password=password)

        # Wait short time for function to start
        time.sleep(0.1)

        for i in range(0, 10):
            serial_console_proxy.proxy.write(
                f'Nonsense non matching line {i}...')
            time.sleep(0.01)

        serial_console_proxy.proxy.write(user_match)

        # Wait for response
        time.sleep(0.01)

        received = serial_console_proxy.proxy.read()
        expected = f'{username}{serial_console_proxy.console.linesep}'

        assert received == expected

        serial_console_proxy.proxy.write(pass_match)

        # Wait for response
        time.sleep(0.01)

        received = serial_console_proxy.proxy.read()
        expected = f'{password}{serial_console_proxy.console.linesep}'

        assert received == expected

        # Wait for console.login() to finish
        async_result.get()

        # If we've gotten to here without error then success
        assert True


def test_SerialConsole_login_no_exception_on_success_with_success_match(serial_console_proxy):
        user_match = 'Enter username: '
        pass_match = 'Enter password: '
        success_match = 'command prompt >>'
        username = 'Foo'
        password = 'Bar'

        async_result = nonblocking(
            serial_console_proxy.console.login,
            username_match=user_match,
            password_match=pass_match,
            username=username,
            password=password,
            success_match=success_match)

        # Wait short time for function to start
        time.sleep(0.1)

        for i in range(0, 10):
            serial_console_proxy.proxy.write(
                f'Nonsense non matching line {i}...')
            time.sleep(0.01)

        serial_console_proxy.proxy.write(user_match)

        # Wait for response
        time.sleep(0.01)

        received = serial_console_proxy.proxy.read()
        expected = f'{username}{serial_console_proxy.console.linesep}'

        assert received == expected

        serial_console_proxy.proxy.write(pass_match)

        # Wait for response
        time.sleep(0.01)

        received = serial_console_proxy.proxy.read()
        expected = f'{password}{serial_console_proxy.console.linesep}'

        assert received == expected

        serial_console_proxy.proxy.write(success_match)

        # Wait for response
        time.sleep(0.01)

        # Wait for console.login() to finish
        async_result.get()

        # If we've gotten to here without error then success
        assert True


def test_SerialConsole_login_except_on_wrong_success_match(serial_console_proxy):
        user_match = 'Enter username: '
        pass_match = 'Enter password: '
        success_match = 'command prompt >>'
        username = 'Foo'
        password = 'Bar'

        async_result = nonblocking(
            serial_console_proxy.console.login,
            username_match=user_match,
            password_match=pass_match,
            username=username,
            password=password,
            success_match=success_match)

        # Wait short time for function to start
        time.sleep(0.1)

        for i in range(0, 10):
            serial_console_proxy.proxy.write(
                f'Nonsense non matching line {i}...')
            time.sleep(0.01)

        serial_console_proxy.proxy.write(user_match)

        # Wait for response
        time.sleep(0.01)

        received = serial_console_proxy.proxy.read()
        expected = f'{username}{serial_console_proxy.console.linesep}'

        assert received == expected

        serial_console_proxy.proxy.write(pass_match)

        # Wait for response
        time.sleep(0.01)

        received = serial_console_proxy.proxy.read()
        expected = f'{password}{serial_console_proxy.console.linesep}'

        assert received == expected

        serial_console_proxy.proxy.write(
            'This is not the success_match you are looking for')

        with pytest.raises(ConsoleLoginFailedError):
            # Wait for console.login() to finish
            async_result.get()


def test_SerialConsole_login_except_on_wrong_username_match(serial_console_proxy):
        user_match = 'Enter username: '
        username = 'Foo'

        async_result = nonblocking(
            serial_console_proxy.console.login,
            username_match=user_match,
            username=username)

        # Wait short time for function to start
        time.sleep(0.1)

        for i in range(0, 10):
            serial_console_proxy.proxy.write(
                f'Nonsense non matching line {i}...')
            time.sleep(0.01)

        serial_console_proxy.proxy.write(
            'This is not the username_match you are looking for')

        with pytest.raises(ConsoleLoginFailedError):
            # Wait for console.login() to finish
            async_result.get()