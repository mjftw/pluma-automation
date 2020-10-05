import os
import pytest
import json

from pluma.cli.plugins import load_plugin_modules


PLUGIN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins-src')
TEST_YAML = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugin-test.yml')
TARGET_YAML = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugin-test-target.yml')


def test_load_plugin_should_run_module_init(capsys):
    load_plugin_modules(PLUGIN_DIR)
    assert 'hello from module init\n' == capsys.readouterr().out


def test_cli_should_error_on_missing_test_config(pluma_cli):
    with pytest.raises(RuntimeError):
        pluma_cli(['--config', '/this-file-doesnt-exist!'])


def test_cli_should_error_on_missing_target_config(pluma_cli):
    with pytest.raises(RuntimeError):
        pluma_cli(['--target', '/this-file-doesnt-exist!'])


def test_cli_should_find_test_from_plugins_dir(pluma_cli):
    pluma_cli(['--config', TEST_YAML, '--target', TARGET_YAML, '--plugin', PLUGIN_DIR])


def test_cli_should_create_results_file(pluma_cli, pluma_config_file, temp_file):
    results_file = 'results-test.json'
    config = pluma_config_file(settings={
        'results': {
            'file': results_file
        }})

    pluma_cli(['--config', config, '--target', temp_file()])

    try:
        assert os.path.isfile(results_file)
    finally:
        if os.path.isfile(results_file):
            os.remove(results_file)


def test_cli_should_create_valid_json_results_file(pluma_cli, pluma_config_file, temp_file):
    results_file = 'results-test.json'
    config = pluma_config_file(settings={
        'results': {
            'file': results_file
        }})

    pluma_cli(['--config', config, '--target', temp_file()])

    with open(results_file, 'r') as f:
        assert json.load(f)
