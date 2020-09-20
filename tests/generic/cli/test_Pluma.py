from os import path
import pytest

from pluma.cli import Pluma, ConfigurationError, TestsConfigError, TargetConfigError


def run_all(test_file: str, target_file: str):
    config_folder = path.join(path.os.path.dirname(__file__), 'test-configs/')

    Pluma.execute_tests(path.join(config_folder, f'{test_file}.yml'),
                        path.join(config_folder, f'{target_file}.yml'))
    Pluma.execute_run(path.join(config_folder, f'{test_file}.yml'),
                      path.join(config_folder, f'{target_file}.yml'), check_only=True)


def test_Pluma_minimal():
    run_all('minimal-tests', 'minimal-target')


def test_Pluma_works_with_samples():
    run_all('sample-tests', 'sample-target')


def test_Pluma_variable_substitution():
    run_all('variable-sub-tests', 'variable-sub-target')


def test_Pluma_tests_error_on_unknown_action():
    with pytest.raises(TestsConfigError):
        run_all('invalid-action-tests', 'minimal-target')


def test_Pluma_tests_error_on_unknown_attribute():
    with pytest.raises(ConfigurationError):
        run_all('invalid-attributes-tests', 'minimal-target')


def test_Pluma_target_error_on_unknown_attribute():
    with pytest.raises(TargetConfigError):
        run_all('minimal-tests', 'invalid-attributes-target')
