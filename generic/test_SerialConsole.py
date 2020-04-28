import os
import time

from generic_fixtures import serial_console_proxy
from utils import nonblocking


def test_SerialConsole_send_sends_data(serial_console_proxy):
    serial_console_proxy.console.send('Foo')

    written = serial_console_proxy.proxy.read()

    assert written


def test_SerialConsole_send_sends_correct_data(serial_console_proxy):
    msg = 'Foo'
    serial_console_proxy.console.send(msg)

    written = serial_console_proxy.proxy.read(
        encoding=serial_console_proxy.console.encoding)

    assert written == '{}{}'.format(msg, serial_console_proxy.console.linesep)


def test_SerialConsole_send_doesnt_send_newline_when_send_newline_arg_false(serial_console_proxy):
    msg = 'Foo'
    serial_console_proxy.console.send(msg, send_newline=False)

    written = serial_console_proxy.proxy.read(
        encoding=serial_console_proxy.console.encoding)

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

    serial_console_proxy.proxy.write(msg, serial_console_proxy.console.encoding)

    received, __ = async_result.get()
    assert received == msg