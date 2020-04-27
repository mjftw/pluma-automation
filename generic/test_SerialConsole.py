import os

from generic_fixtures import serial_console_proxy


def test_SerialConsole_send_sends_data(serial_console_proxy):
    serial_console_proxy.console.send('Foo')

    written = serial_console_proxy.proxy.read()

    assert written


def test_SerialConsole_send_sends_correct_data(serial_console_proxy):
    msg = 'Foo'
    serial_console_proxy.console.send(msg)

    written = serial_console_proxy.proxy.read()

    assert written.decode(serial_console_proxy.console.encoding) == '{}{}'.format(
        msg, serial_console_proxy.console.linesep)
