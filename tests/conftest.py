import sys
import pytest


def platform_is_rpi():
    # Cheap check, could check platform instead, but this works for the most part
    return 'RPi.GPIO' in sys.modules


def pytest_collection_modifyitems(config, items):
    for item in items:
        # Don't run rpi tests if not on Raspberry Pi
        if item.parent.name.startswith('rpi/') and not platform_is_rpi():
            item.add_marker(pytest.mark.skip('Skipping rpi tests as not on Raspberry Pi'))