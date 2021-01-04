from pluma.core.baseclasses import Logger
from pluma.cli import Configuration, DeviceActionRegistry, TestsConfigError
from .config import TestDefinition, TestsProvider

log = Logger()

CONFIGURATION_SECTION = 'macros'
CONFIGURATION_SEQUENCE_KEY = 'run_macro'


class Macro:
    def __init__(self, name: str, sequence: list):
        self.name = name
        self.sequence = sequence


class MacroProvider(TestsProvider):
    def __init__(self):
        pass

    def display_name(self):
        return 'Macros'

    def consume_config(self, config: Configuration):
        macros_config = config.pop('macros')
        for macro_config in macros_config:
            self.add_macro(self.macro_from_config(macro_config))

    @staticmethod
    def macro_from_config(macro_config: dict) -> Macro:
        if not isinstance(macro_config, dict):
            raise TestsConfigError(
                f'Invalid macro "{macro_config}", which is not a dictionary')

        config = Configuration(macro_config)
        macro = Macro(config.pop('name'), config.pop('sequence'))
        config.ensure_consumed()
        return macro

    def add_macro(self, macro: Macro):
        pass

    def configuration_key(self):
        return CONFIGURATION_SEQUENCE_KEY

    def all_tests(self, key: str, config):
        parameter_set = None
        if config:
            if not isinstance(config, Configuration):
                parameter_set = config
            else:
                parameter_set = config.content()

        return [TestDefinition(key, testclass=DeviceActionRegistry.action_class(key),
                               test_provider=self, parameter_sets=[parameter_set], selected=True)]
