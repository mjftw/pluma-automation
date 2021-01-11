from typing import List

from pluma.core.baseclasses import Logger
from pluma.cli import Configuration, DeviceActionRegistry
from .config import TestDefinition, TestsProvider

log = Logger()


class DeviceActionProvider(TestsProvider):
    def __init__(self):
        pass

    def display_name(self) -> str:
        return 'Device actions'

    def configuration_key(self) -> List[str]:
        return DeviceActionRegistry.all_actions()

    def all_tests(self, key: str, config: Configuration) -> List[TestDefinition]:
        parameter_set = None
        if config:
            if not isinstance(config, Configuration):
                parameter_set = config
            else:
                parameter_set = config.content()

        return [TestDefinition(key, testclass=DeviceActionRegistry.action_class(key),
                               test_provider=self, parameter_sets=[parameter_set], selected=True)]
