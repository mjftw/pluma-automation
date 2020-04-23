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
