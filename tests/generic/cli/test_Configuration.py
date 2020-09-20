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


def test_TestsConfig_len(minimal_config):
    assert len(minimal_config) == len(MINIMAL_CONFIG_DICT)


def test_TestsConfig_content(minimal_config):
    assert minimal_config.content() == MINIMAL_CONFIG_DICT


def test_TestsConfig_pop(minimal_config):
    assert minimal_config.pop(ATTRIBUTE1) == ATTRIBUTE1_VALUE
    assert len(minimal_config) == len(MINIMAL_CONFIG_DICT)-1

    assert minimal_config.pop(ATTRIBUTE1) is None


def test_TestsConfig_pop_dict(minimal_config):
    assert minimal_config.pop(ATTRIBUTE2) == Configuration(ATTRIBUTE2_DICT)


def test_TestsConfig_pop_raw(minimal_config):
    assert minimal_config.pop_raw(ATTRIBUTE2) == ATTRIBUTE2_DICT


def test_TestsConfig_ensure_consume_should_error_on_uncomsumed(minimal_config):
    with pytest.raises(ConfigurationError):
        minimal_config.ensure_consumed()


def test_TestsConfig_ensure_consume_should_no_error_when_empty(minimal_config):
    minimal_config.pop(ATTRIBUTE1)
    minimal_config.pop(ATTRIBUTE2)
    assert len(minimal_config) == 0
    minimal_config.ensure_consumed()
