import re
from farmcore import USBRelay, Hub
from pytest import fixture

from config import read_config
from schema import check_schema


def usb_path_regex():
    return re.compile(r'([-.]{0,1}[1-9]+)+')


def read_config_usb_path(name):
    assert isinstance(name, str)

    conf = read_config()

    check_schema(conf,
        {
            'usb_paths': {
                name: usb_path_regex()
            }
        }
    )

    return conf['usb_paths'][name]


@fixture
def relay_pins():
    conf = read_config()

    check_schema(conf,
        {
            "board_pins" : {
                "usb_relay": {
                    "1": {
                        "A": int,
                        "Common": int
                    },
                    "4": {
                        "B": int,
                        "Common": int
                    }
                }
            }
        }
    )

    return conf['board_pins']['usb_relay']


@fixture
def usb_relay():
    return USBRelay(read_config_usb_path('relay'))


@fixture
def hub():
    return Hub(read_config_usb_path('hub'))


@fixture
def hub_serial_path():
    return read_config_usb_path('hub_serial')


@fixture
def hub_relay_path():
    return read_config_usb_path('hub_relay')
