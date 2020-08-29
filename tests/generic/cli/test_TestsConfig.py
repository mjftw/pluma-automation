import copy
import pytest
from pytest import fixture
from unittest.mock import MagicMock

from pluma.cli import TestsConfig, Configuration, TestsProvider, TestsConfigError

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


@fixture
def minimal_testsconfig():
    return TestsConfig(Configuration(copy.deepcopy(MINIMAL_CONFIG)),
                       [MockTestsProvider()])


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


def test_TestsConfig__supported_actions_should_return_key_provider_dict():
    provider1_key1 = 'abc'
    provider1_key2 = 'def'
    provider1 = MagicMock(MockTestsProvider)
    provider1.configuration_key.return_value = [provider1_key1, provider1_key2]

    provider2_key = '123'
    provider2 = MagicMock(MockTestsProvider)
    provider2.configuration_key.return_value = provider2_key

    actions = TestsConfig._supported_actions([provider1, provider2])
    assert actions == {
        provider1_key1: provider1,
        provider1_key2: provider1,
        provider2_key: provider2
    }


def test_TestsConfig___supported_actions_should_error_on_already_registered_key():
    action_key = 'same_key'
    provider1 = MagicMock(MockTestsProvider)
    provider1.configuration_key.return_value = ['abc', action_key]

    provider2 = MagicMock(MockTestsProvider)
    provider2.configuration_key.return_value = action_key

    with pytest.raises(TestsConfigError):
        TestsConfig._supported_actions([provider1, provider2])


def test_TestsConfig_tests_from_action_should_return_all_tests():
    provider = MagicMock(MockTestsProvider)
    all_tests_return = [1, 2, 3]
    action_key = 'some_key'
    provider.configuration_key.return_value = action_key
    provider.all_tests.return_value = all_tests_return

    tests = TestsConfig.tests_from_action(action_key, {'some': 'settings'},
                                          {action_key: provider})
    assert tests == all_tests_return


def test_TestsConfig_tests_from_action_should_error_if_action_unsupported():
    with pytest.raises(TestsConfigError):
        TestsConfig.tests_from_action('abc', {'some': 'settings'}, {'def': MockTestsProvider})
