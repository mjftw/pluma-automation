import os

from farmcore.baseclasses import Logger
from farmtest import ShellTest
from farmcli import Configuration, TestsConfigError
from .config import TestDefinition, TestsProvider

log = Logger()


class ShellTestsProvider(TestsProvider):
    def __init__(self):
        pass

    def display_name(self):
        return 'Inline tests (pluma.yml, Shell)'

    def configuration_key(self):
        return 'shell_tests'

    def all_tests(self, config):
        if not config:
            return []

        if isinstance(config, Configuration):
            config = config.content()

        selected_tests = []
        for test_name in config:
            try:
                test_parameters = config[test_name]
                test_parameters['name'] = test_name
                test = TestDefinition(test_name, testclass=ShellTest, test_provider=self,
                                      parameter_sets=[test_parameters], selected=True)
                selected_tests.append(test)
            except Exception as e:
                raise TestsConfigError(
                    f'Failed to parse script test "{test_name}":{os.linesep}    {e}')

        return selected_tests
