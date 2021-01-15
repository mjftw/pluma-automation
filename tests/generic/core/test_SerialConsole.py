import os
import pytest
import tempfile
import time
from pluma.core.exceptions import ConsoleLoginFailedError
from pluma.core import SerialConsole

from utils import nonblocking
from loremipsum import loremipsum


def test_SerialConsole_send_sends_data(serial_console_proxy):
    serial_console_proxy.console.send('Foo')

    written = serial_console_proxy.read_serial_output()

    assert written


def test_SerialConsole_send_sends_correct_data(serial_console_proxy):
    msg = loremipsum
    serial_console_proxy.console.send(msg)

    written = serial_console_proxy.read_serial_output()

    assert written == f'{msg}{serial_console_proxy.console.engine.linesep}'


def test_SerialConsole_check_alive_returns_true_when_target_responds(serial_console_proxy):
    async_result = nonblocking(
        serial_console_proxy.console.check_alive)

    # Send console a newline char
    serial_console_proxy.fake_reception(serial_console_proxy.console.engine.linesep)

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

    nonblocking(
        serial_console_proxy.console.login,
        username_match=user_match,
        username=username)

    # Expect line break, to force printing the prompt
    received = serial_console_proxy.read_serial_output()
    expected = f'{serial_console_proxy.console.engine.linesep}'

    assert received == expected

    for i in range(0, 10):
        serial_console_proxy.fake_reception(
            f'Nonsense non matching line {i}...')
        time.sleep(0.01)

    serial_console_proxy.fake_reception(user_match)

    received = serial_console_proxy.read_serial_output()
    expected = f'{username}{serial_console_proxy.console.engine.linesep}'

    assert received == expected


def test_SerialConsole_login_success_with_no_password(serial_console_proxy):
    user_match = 'Enter username: '
    username = 'Foo'

    async_result = nonblocking(
        serial_console_proxy.console.login,
        username_match=user_match,
        username=username)

    # Expect line break, used to force printing the prompt
    received = serial_console_proxy.read_serial_output()
    expected = f'{serial_console_proxy.console.engine.linesep}'

    assert received == expected

    for i in range(0, 10):
        serial_console_proxy.fake_reception(
            f'Nonsense non matching line {i}...')
        time.sleep(0.01)

    serial_console_proxy.fake_reception(user_match)

    received = serial_console_proxy.read_serial_output()
    expected = f'{username}{serial_console_proxy.console.engine.linesep}'

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

    nonblocking(
        serial_console_proxy.console.login,
        username_match=user_match,
        password_match=pass_match,
        username=username,
        password=password)

    # Expect line break, used to force printing the prompt
    received = serial_console_proxy.read_serial_output()
    expected = f'{serial_console_proxy.console.engine.linesep}'

    assert received == expected

    for i in range(0, 10):
        serial_console_proxy.fake_reception(
            f'Nonsense non matching line {i}...')
        time.sleep(0.01)

    serial_console_proxy.fake_reception(user_match)

    received = serial_console_proxy.read_serial_output()
    expected = f'{username}{serial_console_proxy.console.engine.linesep}'

    assert received == expected

    serial_console_proxy.fake_reception(pass_match)

    received = serial_console_proxy.read_serial_output()
    expected = f'{password}{serial_console_proxy.console.engine.linesep}'

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

    # Expect line break, used to force printing the prompt
    received = serial_console_proxy.read_serial_output()
    expected = f'{serial_console_proxy.console.engine.linesep}'

    assert received == expected

    for i in range(0, 10):
        serial_console_proxy.fake_reception(
            f'Nonsense non matching line {i}...')
        time.sleep(0.01)

    serial_console_proxy.fake_reception(user_match)

    received = serial_console_proxy.read_serial_output()
    expected = f'{username}{serial_console_proxy.console.engine.linesep}'

    assert received == expected

    serial_console_proxy.fake_reception(pass_match)

    received = serial_console_proxy.read_serial_output()
    expected = f'{password}{serial_console_proxy.console.engine.linesep}'

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

    # Expect line break, used to force printing the prompt
    received = serial_console_proxy.read_serial_output()
    expected = f'{serial_console_proxy.console.engine.linesep}'

    assert received == expected

    for i in range(0, 10):
        serial_console_proxy.fake_reception(
            f'Nonsense non matching line {i}...')
        time.sleep(0.01)

    serial_console_proxy.fake_reception(user_match)

    received = serial_console_proxy.read_serial_output()
    expected = f'{username}{serial_console_proxy.console.engine.linesep}'

    assert received == expected

    serial_console_proxy.fake_reception(pass_match)

    received = serial_console_proxy.read_serial_output()
    expected = f'{password}{serial_console_proxy.console.engine.linesep}'

    assert received == expected

    serial_console_proxy.fake_reception(success_match)

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

    # Expect line break, used to force printing the prompt
    received = serial_console_proxy.read_serial_output()
    expected = f'{serial_console_proxy.console.engine.linesep}'

    assert received == expected

    for i in range(0, 10):
        serial_console_proxy.fake_reception(
            f'Nonsense non matching line {i}...')
        time.sleep(0.01)

    serial_console_proxy.fake_reception(user_match)

    received = serial_console_proxy.read_serial_output()
    expected = f'{username}{serial_console_proxy.console.engine.linesep}'

    assert received == expected

    serial_console_proxy.fake_reception(pass_match)

    received = serial_console_proxy.read_serial_output()
    expected = f'{password}{serial_console_proxy.console.engine.linesep}'

    assert received == expected

    serial_console_proxy.fake_reception(
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

    for i in range(0, 10):
        serial_console_proxy.fake_reception(
            f'Nonsense non matching line {i}...')

    serial_console_proxy.fake_reception(
        'This is not the username_match you are looking for')

    with pytest.raises(ConsoleLoginFailedError):
        # Wait for console.login() to finish
        async_result.get()


def test_SerialConsole_does_not_require_login(serial_console_proxy):
    assert serial_console_proxy.console.requires_login is True


def test_SerialConsole_raw_log_file(pty_pair):
    received = 'abcd\nefgh'

    with tempfile.NamedTemporaryFile() as tmpfile:
        console = SerialConsole(port=os.ttyname(pty_pair.secondary.fd), baud=115200,
                                encoding='utf-8', raw_logfile=tmpfile.name)

        console.open()
        pty_pair.main.write(received)
        console.read_all()
        console.close()

        assert tmpfile.read() == received.encode(console.engine.encoding)
