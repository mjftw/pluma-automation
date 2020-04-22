from farmcore import USBRelay, Hub
from pytest import fixture
import os
import json


HARDWARE_CONF = os.path.join(
    os.path.dirname(
        os.path.realpath(__file__)
    ),
    'hardware.json'
)


def read_config():
    with open(HARDWARE_CONF, 'r') as f:
        return json.load(f)


@fixture
def relay_pins():
    conf = read_config()

    # Check config file has reqired settings
    try:
        assert 'board_pins' in conf
        assert 'usb_relay' in conf['board_pins']
        assert '1' in conf['board_pins']['usb_relay']
        assert 'A' in conf['board_pins']['usb_relay']['1']
        assert 'Common' in conf['board_pins']['usb_relay']['1']
        assert '4' in conf['board_pins']['usb_relay']
        assert 'Common' in conf['board_pins']['usb_relay']['4']
        assert 'B' in conf['board_pins']['usb_relay']['4']
    except AssertionError:
        raise RuntimeError(f'Incorrect hardware config in {HARDWARE_CONF}')

    return conf['board_pins']['usb_relay']


@fixture
def usb_relay():
    conf = read_config()

    # Check config file has reqired settings
    try:
        assert 'usb_paths' in conf
        assert 'usb_relay' in conf['usb_paths']
    except AssertionError:
        raise RuntimeError(f'Incorrect hardware config in {HARDWARE_CONF}')

    return USBRelay(conf['usb_paths']['usb_relay'])