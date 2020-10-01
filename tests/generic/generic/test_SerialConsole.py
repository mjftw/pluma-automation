import time
import pytest
from pluma.core.exceptions import ConsoleLoginFailedError

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

    assert written == f'{msg}{serial_console_proxy.console.interactor.linesep}'


def test_SerialConsole_send_doesnt_send_newline_when_send_newline_arg_false(serial_console_proxy):
    msg = loremipsum
    serial_console_proxy.console.send(msg, send_newline=False)

    written = serial_console_proxy.read_serial_output()

    assert written == msg


def test_SerialConsole_read_all_returns_all_data(serial_console_proxy):
    msg = 'Bar'

    serial_console_proxy.console.open()
    serial_console_proxy.fake_reception(msg)
    received = serial_console_proxy.console.read_all()

    assert received == msg


def test_SerialConsole_send_and_expect_returns_matched_when_match_available(
        serial_console_proxy):
    before_match, to_match = 'Foo', 'Bar'
    msg = before_match + to_match

    async_result = nonblocking(serial_console_proxy.console.send_and_expect,
                               cmd='', match=to_match)

    # Wait short time for function to start
    time.sleep(0.1)

    serial_console_proxy.fake_reception(msg)

    __, matched = async_result.get()
    assert matched == to_match


def test_SerialConsole_send_and_expect_returns_received_when_match_available(
        serial_console_proxy):
    before_match, to_match = 'Foo', 'Bar'
    msg = before_match + to_match

    async_result = nonblocking(serial_console_proxy.console.send_and_expect,
                               cmd='', match=to_match)

    # Wait short time for function to start
    time.sleep(0.1)

    serial_console_proxy.fake_reception(msg)

    received, __ = async_result.get()
    assert received == msg


def test_SerialConsole_send_and_expect_returns_received_none_when_no_match_available(
        serial_console_proxy):
    msg = loremipsum
    wont_match = 'Baz'

    async_result = nonblocking(serial_console_proxy.console.send_and_expect,
                               cmd='', match=wont_match, timeout=0.5)

    serial_console_proxy.fake_reception(msg)

    __, matched = async_result.get()
    assert matched is None


def test_SerialConsole_send_and_expect_returns_received_when_no_match_available(serial_console_proxy):
    msg = loremipsum
    wont_match = 'Baz'

    async_result = nonblocking(serial_console_proxy.console.send_and_expect,
                               cmd='', match=wont_match, timeout=0.5)

    serial_console_proxy.fake_reception(msg)

    received, __ = async_result.get()
    assert received == msg


def test_SerialConsole_send_matches_regex(serial_console_proxy):
    msg = 'Hello World! 123FooBarBaz'
    regex = '[0-3]+Foo'
    expected_match = '123Foo'

    async_result = nonblocking(serial_console_proxy.console.send_and_expect,
                               cmd='', match=regex)

    serial_console_proxy.fake_reception(msg)

    __, matched = async_result.get()
    assert matched == expected_match


def test_SerialConsole_send_and_expect_matches_regex(serial_console_proxy):
    expected_match = '123Match'
    expected_received = f'Multiline content\n and {expected_match}'
    regex = '[0-3]+Match'

    send_and_expect_result = nonblocking(serial_console_proxy.console.send_and_expect,
                                         cmd='abc', match=regex)

    serial_console_proxy.fake_reception(expected_received+'Trailing content')

    received, matched = send_and_expect_result.get()
    assert received == expected_received
    assert matched == expected_match


def test_SerialConsole_send_and_expect_matches_regex_with_previous_content(
        serial_console_proxy):
    expected_match = '123Match'
    expected_received = f'Multiline content\n and {expected_match}'
    regex = '[0-3]+Match'

    serial_console_proxy.fake_reception('Some content sent before trying to match')

    send_and_expect_result = nonblocking(serial_console_proxy.console.send_and_expect,
                                         cmd='abc', match=regex)

    serial_console_proxy.fake_reception(expected_received)

    received, matched = send_and_expect_result.get()
    assert received == expected_received
    assert matched == expected_match


def test_SerialConsole_send_and_expect_returns_received_if_no_match(serial_console_proxy):
    expected_received = 'Not really matching.'
    regex = 'A regex'

    send_and_expect_result = nonblocking(serial_console_proxy.console.send_and_expect,
                                         cmd='abc', match=regex, timeout=0.5)

    serial_console_proxy.fake_reception(expected_received)

    received, matched = send_and_expect_result.get()
    assert received == expected_received
    assert matched is None


def test_SerialConsole_send_and_expect_ignores_previous_content(serial_console_proxy):
    expected_received = 'Not really matching.'
    regex = '[0-3]+Match'

    serial_console_proxy.fake_reception(expected_received)

    send_and_expect_result = nonblocking(serial_console_proxy.console.send_and_expect,
                                         cmd='abc', match=regex, timeout=0.5)

    received, matched = send_and_expect_result.get()
    assert received == received
    assert matched is None


@pytest.mark.parametrize('timeout', [0.2, 1])
def test_SerialConsole_send_and_expect_returns_after_timeout(serial_console_proxy, timeout):
    start_time = time.time()

    send_and_expect_result = nonblocking(serial_console_proxy.console.send_and_expect,
                                         cmd='abc', match='NoFoo', timeout=timeout)

    serial_console_proxy.fake_reception('abc\ndef')

    send_and_expect_result.get()
    total_duration = time.time() - start_time

    assert 0.8 * timeout < total_duration < 1.2*timeout


def test_SerialConsole_check_alive_returns_true_when_target_responds(serial_console_proxy):
    async_result = nonblocking(
        serial_console_proxy.console.check_alive)

    # Send console a newline char
    serial_console_proxy.fake_reception(serial_console_proxy.console.interactor.linesep)

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
    expected = f'{serial_console_proxy.console.interactor.linesep}'

    assert received == expected

    for i in range(0, 10):
        serial_console_proxy.fake_reception(
            f'Nonsense non matching line {i}...')
        time.sleep(0.01)

    serial_console_proxy.fake_reception(user_match)

    received = serial_console_proxy.read_serial_output()
    expected = f'{username}{serial_console_proxy.console.interactor.linesep}'

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
    expected = f'{serial_console_proxy.console.interactor.linesep}'

    assert received == expected

    for i in range(0, 10):
        serial_console_proxy.fake_reception(
            f'Nonsense non matching line {i}...')
        time.sleep(0.01)

    serial_console_proxy.fake_reception(user_match)

    received = serial_console_proxy.read_serial_output()
    expected = f'{username}{serial_console_proxy.console.interactor.linesep}'

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
    expected = f'{serial_console_proxy.console.interactor.linesep}'

    assert received == expected

    for i in range(0, 10):
        serial_console_proxy.fake_reception(
            f'Nonsense non matching line {i}...')
        time.sleep(0.01)

    serial_console_proxy.fake_reception(user_match)

    received = serial_console_proxy.read_serial_output()
    expected = f'{username}{serial_console_proxy.console.interactor.linesep}'

    assert received == expected

    serial_console_proxy.fake_reception(pass_match)

    received = serial_console_proxy.read_serial_output()
    expected = f'{password}{serial_console_proxy.console.interactor.linesep}'

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
    expected = f'{serial_console_proxy.console.interactor.linesep}'

    assert received == expected

    for i in range(0, 10):
        serial_console_proxy.fake_reception(
            f'Nonsense non matching line {i}...')
        time.sleep(0.01)

    serial_console_proxy.fake_reception(user_match)

    received = serial_console_proxy.read_serial_output()
    expected = f'{username}{serial_console_proxy.console.interactor.linesep}'

    assert received == expected

    serial_console_proxy.fake_reception(pass_match)

    received = serial_console_proxy.read_serial_output()
    expected = f'{password}{serial_console_proxy.console.interactor.linesep}'

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
    expected = f'{serial_console_proxy.console.interactor.linesep}'

    assert received == expected

    for i in range(0, 10):
        serial_console_proxy.fake_reception(
            f'Nonsense non matching line {i}...')
        time.sleep(0.01)

    serial_console_proxy.fake_reception(user_match)

    received = serial_console_proxy.read_serial_output()
    expected = f'{username}{serial_console_proxy.console.interactor.linesep}'

    assert received == expected

    serial_console_proxy.fake_reception(pass_match)

    received = serial_console_proxy.read_serial_output()
    expected = f'{password}{serial_console_proxy.console.interactor.linesep}'

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
    expected = f'{serial_console_proxy.console.interactor.linesep}'

    assert received == expected

    for i in range(0, 10):
        serial_console_proxy.fake_reception(
            f'Nonsense non matching line {i}...')
        time.sleep(0.01)

    serial_console_proxy.fake_reception(user_match)

    received = serial_console_proxy.read_serial_output()
    expected = f'{username}{serial_console_proxy.console.interactor.linesep}'

    assert received == expected

    serial_console_proxy.fake_reception(pass_match)

    received = serial_console_proxy.read_serial_output()
    expected = f'{password}{serial_console_proxy.console.interactor.linesep}'

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


def test_SerialConsole_read_all_clears_buffer(serial_console_proxy):
    # Send console a newline char
    serial_console_proxy.fake_reception(serial_console_proxy.console.interactor.linesep)

    time.sleep(0.01)

    serial_console_proxy.console.read_all()

    data_received = serial_console_proxy.console.wait_for_bytes(timeout=0.5)

    assert data_received is False


def test_SerialConsole_read_all_returns_received(serial_console_proxy):
    data1 = 'Line1'

    serial_console_proxy.console.open()
    serial_console_proxy.fake_reception(data1)

    assert serial_console_proxy.console.read_all() == data1


def test_SerialConsole_read_all_clears_received(serial_console_proxy):
    data1 = 'Line1'

    serial_console_proxy.console.open()
    serial_console_proxy.fake_reception(data1)

    assert serial_console_proxy.console.read_all() != ''
    assert serial_console_proxy.console.read_all() == ''


def test_SerialConsole_read_all_preserve_buffer(serial_console_proxy):
    data2 = 'Line2'
    serial_console_proxy.console.open()
    serial_console_proxy.fake_reception(data2)

    assert serial_console_proxy.console.read_all(
        preserve_read_buffer=True) == data2
    assert serial_console_proxy.console.read_all(
        preserve_read_buffer=True) == data2
    assert serial_console_proxy.console.read_all() == data2
    assert serial_console_proxy.console.read_all() == ''


@pytest.mark.parametrize('sleep_time', [0.2, 1])
def test_ConsoleBase_wait_for_quiet_should_wait_at_least_sleep_time(serial_console_proxy,
                                                                    sleep_time):
    serial_console_proxy.console.open()

    start = time.time()
    success = serial_console_proxy.console.wait_for_quiet(quiet=0, sleep_time=sleep_time, timeout=2)
    elapsed = time.time() - start

    assert success is True
    assert 0.8*sleep_time < elapsed < 1.2*sleep_time


@pytest.mark.parametrize('timeout', [0.2, 1])
def test_ConsoleBase_wait_for_quiet_should_wait_at_most_timeout(serial_console_proxy, timeout):
    serial_console_proxy.console.open()

    start = time.time()
    success = serial_console_proxy.console.wait_for_quiet(quiet=timeout*2, timeout=timeout)
    elapsed = time.time() - start

    assert success is False
    assert 0.8*timeout < elapsed < 1.2*timeout


@pytest.mark.parametrize('quiet_time, non_quiet_time', [(0.2, 0.5), (0.5, 1)])
def test_ConsoleBase_wait_for_quiet_should_return_when_quiet(serial_console_proxy,
                                                             quiet_time, non_quiet_time):
    serial_console_proxy.console.open()

    start = time.time()
    async_result = nonblocking(serial_console_proxy.console.wait_for_quiet,
                               quiet=quiet_time, timeout=5)

    data_start = time.time()
    data_end = data_start + non_quiet_time
    while(time.time() < data_end):
        serial_console_proxy.fake_reception('abc', wait_time=0.02)

    success = async_result.get()
    elapsed = time.time() - start

    assert success is True
    total_time = non_quiet_time+quiet_time
    assert 0.8*total_time < elapsed < 1.2*total_time


def test_SerialConsole_does_not_require_login(serial_console_proxy):
    assert serial_console_proxy.console.requires_login is True
