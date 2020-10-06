import os
import pytest
import json

from pluma.cli.plugins import load_plugin_modules
from pluma import plugins


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


def test_cli_should_create_results_file_with_correct_data(pluma_cli, pluma_config_file, temp_file):
    load_plugin_modules(PLUGIN_DIR)


    results_file = 'results-test.json'
    config = pluma_config_file(
        core_tests_params=[(
            plugins.example_plugin.Maths, {'x': 1}
        )],
        settings={
            'iterations': 3,
            'results': {
                'file': results_file
        }})

    pluma_cli(['--config', config, '--target', temp_file()])

    expected_data = json.loads('''\
    {
        "example_plugin.maths.Maths": {
            "x_square": {
                "count": {
                    "1.0": 3
                },
                "max": 1.0,
                "min": 1.0,
                "mode": 1.0,
                "mean": 1.0,
                "median": 1.0,
                "stdev": 0.0,
                "variance": 0.0,
                "chunked_mean": [
                    1.0,
                    1.0,
                    1.0
                ]
            },
            "sqrt_x": {
                "count": {
                    "1.0": 3
                },
                "max": 1.0,
                "min": 1.0,
                "mode": 1.0,
                "mean": 1.0,
                "median": 1.0,
                "stdev": 0.0,
                "variance": 0.0,
                "chunked_mean": [
                    1.0,
                    1.0,
                    1.0
                ]
            },
            "sin_x": {
                "count": {
                    "0.02": 3
                },
                "max": 0.02,
                "min": 0.02,
                "mode": 0.02,
                "mean": 0.02,
                "median": 0.02,
                "stdev": 0.0,
                "variance": 0.0,
                "chunked_mean": [
                    0.02,
                    0.02,
                    0.02
                ]
            },
            "cos_x": {
                "count": {
                    "1.0": 3
                },
                "max": 1.0,
                "min": 1.0,
                "mode": 1.0,
                "mean": 1.0,
                "median": 1.0,
                "stdev": 0.0,
                "variance": 0.0,
                "chunked_mean": [
                    1.0,
                    1.0,
                    1.0
                ]
            },
            "mystring": {
                "count": {
                    "Hello": 3
                }
            }
        }
    }''')

    try:
        with open(results_file, 'r') as f:
            data = json.load(f)
            assert data['data'] == expected_data
    finally:
        if os.path.isfile(results_file):
            os.remove(results_file)

def test_cli_should_create_results_file_with_correct_testrunner_data(pluma_cli, pluma_config_file, temp_file):
    load_plugin_modules(PLUGIN_DIR)


    results_file = 'results-test.json'
    config = pluma_config_file(
        core_tests_params=[(
            plugins.example_plugin.Maths, {'x': 1}
        )],
        settings={
            'results': {
                'file': results_file
        }})

    pluma_cli(['--config', config, '--target', temp_file()])

    expected_testrunner_data = json.loads('''\
    {
        "example_plugin.maths.Maths": {
            "tasks": {
                "ran": [
                    "prepare"
                ],
                "failed": {}
            },
            "data": {
                "x_square": 1.0,
                "sqrt_x": 1.0,
                "sin_x": 0.02,
                "cos_x": 1.0,
                "mystring": "Hello"
            },
            "settings": {
                "x": 1
            },
            "order": 0
        }
    }''')

    try:
        with open(results_file, 'r') as f:
            data = json.load(f)
            assert data['results'][0]['TestRunner'] == expected_testrunner_data
    finally:
        if os.path.isfile(results_file):
            os.remove(results_file)

def test_cli_should_create_results_file_with_correct_settings(pluma_cli, pluma_config_file, temp_file):
    load_plugin_modules(PLUGIN_DIR)


    results_file = 'results-test.json'
    config = pluma_config_file(
        core_tests_params=[(
            plugins.example_plugin.Maths, {'x': 1}
        )],
        settings={
            'iterations': 3,
            'results': {
                'file': results_file
        }})

    pluma_cli(['--config', config, '--target', temp_file()])

    expected_settings = json.loads('''\
    {
        "example_plugin.maths.Maths": {
            "x": 1
        }
    }''')

    try:
        with open(results_file, 'r') as f:
            data = json.load(f)
            assert data['settings'] == expected_settings
    finally:
        if os.path.isfile(results_file):
            os.remove(results_file)
