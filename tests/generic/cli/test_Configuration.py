import pytest
import copy
from pytest import fixture
from pluma.cli import Configuration, ConfigurationError

ATTRIBUTE1 = 'att1'
ATTRIBUTE1_VALUE = 5
ATTRIBUTE2 = 'att2'
ATTRIBUTE2_DICT = {'a': 2}

MINIMAL_CONFIG_DICT = {
    ATTRIBUTE1: ATTRIBUTE1_VALUE,
    ATTRIBUTE2: ATTRIBUTE2_DICT
}


@fixture
def minimal_config():
    return Configuration(copy.deepcopy(MINIMAL_CONFIG_DICT))


def test_Configuration_create_from_none():
    Configuration(None)


def test_Configuration_create(minimal_config):
    pass


def test_Configuration_create_invalid():
    with pytest.raises(ValueError):
        Configuration(['a', 'b'])
    with pytest.raises(ValueError):
        Configuration(Configuration(MINIMAL_CONFIG_DICT))


def test_Configuration_len(minimal_config):
    assert len(minimal_config) == len(MINIMAL_CONFIG_DICT)


def test_Configuration_content(minimal_config):
    assert minimal_config.content() == MINIMAL_CONFIG_DICT


def test_Configuration_pop_raw_returns_value(minimal_config):
    assert minimal_config.pop_raw(ATTRIBUTE1) == ATTRIBUTE1_VALUE


def test_Configuration_pop_raw_returns_dict(minimal_config):
    assert minimal_config.pop_raw(ATTRIBUTE2) == ATTRIBUTE2_DICT


def test_Configuration_pop_raw_removes_value(minimal_config):
    assert minimal_config.pop_raw(ATTRIBUTE1)
    assert len(minimal_config) == len(MINIMAL_CONFIG_DICT)-1
    assert minimal_config.pop_raw(ATTRIBUTE1) is None


def test_Configuration_pop_returns_value(minimal_config):
    assert minimal_config.pop(int, ATTRIBUTE1) == ATTRIBUTE1_VALUE


def test_Configuration_pop_returns_config(minimal_config):
    assert minimal_config.pop(Configuration, ATTRIBUTE2) == Configuration(ATTRIBUTE2_DICT)


def test_Configuration_pop_error_if_not_present(minimal_config):
    with pytest.raises(ConfigurationError):
        assert minimal_config.pop(int, 'unexistent')


def test_Configuration_pop_removes_value(minimal_config):
    assert minimal_config.pop(int, ATTRIBUTE1)
    assert len(minimal_config) == len(MINIMAL_CONFIG_DICT)-1

    with pytest.raises(ConfigurationError):
        assert minimal_config.pop(int, ATTRIBUTE1)


def test_Configuration_pop_optional_return_none_if_not_present(minimal_config):
    assert minimal_config.pop_optional(int, 'unexistent') is None


def test_Configuration_pop_int():
    attribute = 'att'
    value = 123
    config = Configuration({attribute: value})
    assert config.pop(int, attribute) == value


def test_Configuration_pop_int_str():
    attribute = 'att'
    value = '123'
    config = Configuration({attribute: value})
    assert config.pop(int, attribute) == int(value)


def test_Configuration_pop_int_fails_if_not_int():
    attribute = 'att'
    value = 'abc'
    config = Configuration({attribute: value})

    with pytest.raises(ConfigurationError):
        config.pop(int, attribute)


def test_Configuration_pop_str():
    attribute = 'att'
    value = 'abc'
    config = Configuration({attribute: value})
    assert config.pop(str, attribute) == value


def test_Configuration_pop_str_fails_if_not_str():
    attribute = 'att'
    value = {'a': 2}
    config = Configuration({attribute: value})
    with pytest.raises(ConfigurationError):
        config.pop(str, attribute)


def test_Configuration_pop_bool():
    attribute = 'att'
    value = True
    config = Configuration({attribute: value})
    assert config.pop(bool, attribute) == value


def test_Configuration_pop_bool_fails_if_not_bool():
    attribute = 'att'
    value = 'abc'
    config = Configuration({attribute: value})
    with pytest.raises(ConfigurationError):
        config.pop(bool, attribute)


def test_Configuration_pop_list():
    attribute = 'att'
    value = ['a', 'b']
    config = Configuration({attribute: value})
    assert config.pop(list, attribute) == value


def test_Configuration_pop_list_fails_if_not_list():
    attribute = 'att'
    value = 'a'
    config = Configuration({attribute: value})
    with pytest.raises(ConfigurationError):
        config.pop(list, attribute)


def test_Configuration_pop_configuration():
    attribute = 'att'
    value = {'a': 2}
    config = Configuration({attribute: value})
    expected_value = Configuration(value)
    assert len(expected_value) == 1
    assert config.pop(Configuration, attribute) == Configuration(value)


def test_Configuration_pop_config_fails_if_not_config():
    attribute = 'att'
    value = 'a'
    config = Configuration({attribute: value})
    with pytest.raises(ConfigurationError):
        config.pop(Configuration, attribute)


def test_TestsConfig_popitem_returns_last_keyvalue_pair(minimal_config):
    assert minimal_config.popitem() == (ATTRIBUTE2, ATTRIBUTE2_DICT)


def test_TestsConfig_popitem_removes_item(minimal_config):
    minimal_config.popitem()
    assert len(minimal_config) == len(MINIMAL_CONFIG_DICT)-1


def test_TestsConfig_popitem_raise_error_if_empty():
    config = Configuration()
    with pytest.raises(KeyError):
        config.popitem()


def test_Configuration_ensure_consume_should_error_on_unconsumed(minimal_config):
    with pytest.raises(ConfigurationError):
        minimal_config.ensure_consumed()


def test_Configuration_ensure_consume_should_no_error_when_empty(minimal_config):
    minimal_config.pop(int, ATTRIBUTE1)
    minimal_config.pop(dict, ATTRIBUTE2)
    assert len(minimal_config) == 0
    minimal_config.ensure_consumed()
