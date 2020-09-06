import os

from pluma.cli.plugins import load_plugin_modules
import pytest


PLUGIN_DIR = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'src')


def test_load_plugin_should_run_module_init():
    with pytest.raises(NotImplementedError):
        load_plugin_modules(PLUGIN_DIR)
