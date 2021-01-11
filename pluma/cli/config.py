import yaml
import json
import os
from typing import Optional, List, TypeVar, Type, Union, overload, cast
from abc import ABC, abstractmethod

from pluma.core.baseclasses import Logger
from pluma.test.testbase import TestBase

log = Logger()


class ConfigurationError(Exception):
    pass


class TargetConfigError(Exception):
    pass


class TestsConfigError(Exception):
    pass


T = TypeVar('T')


class Configuration:
    def __init__(self, config: dict = None):
        config = config or {}
        if not isinstance(config, dict):
            raise ValueError('Configuration class requires a "dict" object')

        self.config = config

    @staticmethod
    def __raise_error(error: str, context: Optional[str]):
        prefix = f'in "{context}", ' if context else ''
        raise ConfigurationError(f'Configuration error: {prefix}{error}')

    def pop(self, datatype: Type[T], attribute: str, context: Optional[str] = None) -> T:
        value = self.pop_optional(datatype, attribute, context=context)
        if value is None:
            self.__raise_error(
                f'attribute "{attribute}" required', context)

        return value

    # Type if default is None
    @overload
    def pop_optional(self, datatype: Type[T], attribute: str, default: None = None,
                     context: Optional[str] = None) -> Optional[T]: ...

    # Type if default is a non-None value
    @overload
    def pop_optional(self, datatype: Type[T], attribute: str,
                     default: T, context: Optional[str] = None) -> T: ...

    # Implementation
    def pop_optional(self, datatype: Type[T], attribute: str, default: Optional[T] = None,
                     context: Optional[str] = None) -> Union[T, Optional[T]]:
        value = self.pop_raw(attribute, default)
        if value is not None and not isinstance(value, datatype):
            converted = False
            try:
                if datatype is int and isinstance(value, str):
                    value = int(value)
                    converted = True
                elif datatype is Configuration and isinstance(value, dict):
                    value = Configuration(value)
                    converted = True
            except ValueError:
                pass

            if not converted:
                expected_type = datatype.__name__
                if datatype is Configuration:
                    expected_type = dict.__name__

                self.__raise_error(f'attribute "{attribute}" should be a {expected_type} '
                                   f'but got "{value}"', context)

        return cast(Union[T, Optional[T]], value)

    def pop_raw(self, attribute: str, default=None):
        return self.config.pop(attribute, default)

    def read_and_keep(self, attribute: str):
        return self.config.get(attribute)

    def __len__(self) -> int:
        return len(self.config)

    def first(self) -> str:
        for key in self.config:
            return key

        raise ConfigurationError('Configuration empty, cannot call "first"')

    def ensure_consumed(self):
        if len(self) > 0:
            unconsumed_data = self.config
            self.config = {}
            raise ConfigurationError(
                'The following configuration attributes were not recognized or not used:'
                f'{os.linesep}{unconsumed_data}')

    def content(self):
        return self.config

    def __str__(self):
        return json.dumps(self.content())

    def __eq__(self, other):
        return self.content() == other.content()


class TestDefinition():
    '''Data class representing a test, its class, and parameters.'''

    def __init__(self, name: str, testclass: Type[TestBase], test_provider: object,
                 parameter_sets: list = None, selected: bool = False):
        if not name or name == '':
            raise ValueError('Test name cannot be empty')

        if not testclass or not test_provider:
            raise ValueError('Test class and test provider must be set')

        self.name = name
        self.testclass = testclass
        self.provider = test_provider
        self.parameter_sets = parameter_sets or []
        self.selected = selected

        if isinstance(self.parameter_sets, dict):
            self.parameter_sets = [self.parameter_sets]
        elif not isinstance(self.parameter_sets, list):
            raise ValueError(
                f'Parameter sets for test "{name}" should be a list of dictionaries')

    def __repr__(self):
        return f'{self.__module__}.{self.__class__.__name__}{self.parameter_sets or ""}'

    @property
    def description(self):
        return self.testclass.description()


class TestsProvider(ABC):
    '''Abstract base class that provides TestDefinition from the configuration

    Classes implementing TestsProvider must provide a unique configuration key
    (configuration_key), and the "all_tests", which returns the list of
    TestDefinition from a configuration.
    '''
    @abstractmethod
    def display_name(self) -> str:
        '''Return a human-friendly name for the provider'''

    @abstractmethod
    def configuration_key(self) -> str:
        '''Return a unique key (string) representing the provider.

        If the configuration key is encountered in the test configuration,
        this provider will be used when creating the tests definition by
        calling "all_tests" and "selected_tests".
        '''

    @abstractmethod
    def all_tests(self, key: str, config: Configuration) -> List[TestDefinition]:
        '''Return all TestDefinition from the "config" provided by the sequence key "key"'''


class ConfigPreprocessor(ABC):
    @abstractmethod
    def preprocess(self, raw_config: str) -> str:
        '''Return an updated configuration from raw text'''
        pass


class PlumaConfig:
    @staticmethod
    def load_configuration(name: str, config_path: str,
                           preprocessor: ConfigPreprocessor = None) -> Configuration:
        return Configuration(PlumaConfig.load_yaml(name, config_path, preprocessor))

    @staticmethod
    def load_yaml(name: str, yaml_file_path: str,
                  preprocessor: ConfigPreprocessor = None) -> dict:
        try:
            with open(yaml_file_path, 'r') as config:
                content = config.read()
                if preprocessor:
                    content = preprocessor.preprocess(content)

                return yaml.load(content, Loader=yaml.FullLoader)
        except FileNotFoundError as e:
            raise ConfigurationError(
                f'{name} "{yaml_file_path}" does not exist') from e
        except yaml.parser.ParserError as e:
            raise ConfigurationError(
                f'Error while parsing {name} "{yaml_file_path}":'
                f'{os.linesep}{e}') from e
        except Exception as e:
            raise ConfigurationError(
                f'An error occurred while opening/parsing {name} "{yaml_file_path}":'
                f'{os.linesep}{e}') from e
