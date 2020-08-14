from farmcore.baseclasses import Logger
from farmcli import Configuration, TestsConfigError, DeviceActionRegistry
from .config import TestDefinition, TestsProvider

log = Logger()


class DeviceActionProvider(TestsProvider):
    def __init__(self):
        pass

    def display_name(self):
        return 'Device actions'

    def configuration_key(self):
        return DeviceActionRegistry.all_actions()

    def all_tests(self, key: str, config):
        parameter_set = config.content() if config else None
        return [TestDefinition({key}, testclass=DeviceActionRegistry.action_class(key), test_provider=self,
                               parameter_sets=[parameter_set], selected=True)]
