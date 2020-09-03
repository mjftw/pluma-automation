import copy
import pytest
from farmcli import TestsConfig, Configuration, TestsProvider

MINIMAL_CONFIG = {
    'sequence': []
}


class MockTestsProvider(TestsProvider):
    def display_name(self):
        return 'Mock provider'

    def configuration_key(self):
        return 'mock_tests'

    def all_tests(self, config: Configuration):
        return []


def test_TestsConfig_init_should_accept_list_of_providers():
    TestsConfig(Configuration(copy.deepcopy(MINIMAL_CONFIG)),
                [MockTestsProvider()])


def test_TestsConfig_init_should_accept_single_provider():
    TestsConfig(Configuration(copy.deepcopy(
        MINIMAL_CONFIG)), MockTestsProvider())


def test_TestsConfig_init_should_error_if_passed_no_config():
    with pytest.raises(ValueError):
        TestsConfig(None, MockTestsProvider())


def test_TestsConfig_init_should_error_if_passed_dict_for_config():
    with pytest.raises(ValueError):
        TestsConfig(None, MockTestsProvider())


def test_TestsConfig_init_should_error_if_passed_no_provider():
    with pytest.raises(ValueError):
        TestsConfig(Configuration(MINIMAL_CONFIG), None)


def test_TestsConfig_init_should_error_if_passed_empty_list_of_providers():
    with pytest.raises(ValueError):
        TestsConfig(Configuration(MINIMAL_CONFIG), [])
