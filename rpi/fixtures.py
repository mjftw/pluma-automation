import re
from farmcore import USBRelay, Hub
from pytest import fixture

from config import read_config
from schema import check_schema


def usb_path_regex():
    return re.compile(r'([-.]{0,1}[1-9]+)+')


@fixture
def relay_pins():
    conf = read_config()

    # Check config file has reqired settings
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
    conf = read_config()

    # Check config file has reqired settings
    check_schema(conf,
        {
            "usb_paths": {
                "usb_relay": usb_path_regex()
            }
        }
    )

    return USBRelay(conf['usb_paths']['usb_relay'])
