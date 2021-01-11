import os
from typing import List

from pluma.core.baseclasses import Logger
from pluma.test import ShellTest
from pluma.cli import Configuration, TestsConfigError
from .config import TestDefinition, TestsProvider

log = Logger()


class ShellTestsProvider(TestsProvider):
    def __init__(self):
        pass

    def display_name(self) -> str:
        return 'Inline tests (pluma.yml, Shell)'

    def configuration_key(self) -> str:
        return 'shell_tests'

    def all_tests(self, key: str, config: Configuration) -> List[TestDefinition]:
        if not config:
            return []

        config_dict = config.content()
        selected_tests = []
        for test_name in config_dict:
            try:
                test_parameters = config_dict[test_name]
                test_parameters['name'] = test_name
                test = TestDefinition(test_name, testclass=ShellTest, test_provider=self,
                                      parameter_sets=[test_parameters], selected=True)
                selected_tests.append(test)
            except Exception as e:
                raise TestsConfigError(
                    f'Failed to parse script test "{test_name}":{os.linesep}    {e}')

        return selected_tests
