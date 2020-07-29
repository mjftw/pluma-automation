import yaml
import json

from farmcli import PlumaLogger

log = PlumaLogger()


class ConfigurationError(Exception):
    pass


class Configuration:
    def __init__(self, config={}):
        if not isinstance(config, dict):
            raise ValueError('Configuration class requires a "dict" object')

        self.config = config

    def pop(self, attribute, default=None):
        value = self.pop_raw(attribute, default)
        if isinstance(value, dict):
            return Configuration(value)

        return value

    def pop_raw(self, attribute, default=None):
        return self.config.pop(attribute, default)

    def read_and_keep(self, attribute):
        return self.config.get(attribute)

    def len(self):
        return len(self.config)

    def first(self):
        for key in self.config:
            return key

    def ensure_consumed(self):
        if self.len() > 0:
            unconsumed_data = self.config
            self.config = {}
            raise ConfigurationError(
                f'The following configuration attributes were not recognized or not used:\n{unconsumed_data}')

    def content(self):
        return self.config

    def __str__(self):
        return json.dumps(self.content())


class PlumaConfig:
    @staticmethod
    def load_configuration(tests_config_path, target_config_path):
        tests_config, target_config = PlumaConfig.load_configuration_raw(
            tests_config_path, target_config_path)

        return Configuration(tests_config), Configuration(target_config)

    @staticmethod
    def load_configuration_raw(tests_config_path, target_config_path):
        tests_config = None
        target_config = None

        try:
            with open(tests_config_path, 'r') as config:
                tests_config = yaml.load(config, Loader=yaml.FullLoader)
        except FileNotFoundError:
            raise ConfigurationError(
                f'Configuration file "{tests_config_path}" does not exist')
        except:
            raise ConfigurationError(
                f'Failed to open configuration file "{tests_config_path}"')

        try:
            with open(target_config_path, 'r') as config:
                target_config = yaml.load(config, Loader=yaml.FullLoader)
        except FileNotFoundError:
            raise ConfigurationError(
                f'Target file "{target_config_path}" does not exist')
        except:
            raise ConfigurationError(
                f'Failed to open target file "{tests_config_path}"')

        return tests_config, target_config
