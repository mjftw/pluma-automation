import re
import inspect
from operator import attrgetter

import pluma.plugins
from pluma.core.baseclasses import Logger
from pluma.test import TestBase
from pluma.cli import Configuration
from .config import TestDefinition, TestsProvider

log = Logger()


class PythonTestsProvider(TestsProvider):
    def __init__(self):
        pass

    def display_name(self):
        return 'Core tests (testsuite, Python)'

    def configuration_key(self):
        return 'core_tests'

    def all_tests(self, key: str, config):
        if not config:
            return []

        include = config.pop('include') or []
        exclude = config.pop('exclude') or []
        parameters = config.pop('parameters') or Configuration()
        all_tests = self.find_python_tests()

        # Instantiate tests selected
        for test in all_tests:
            test.selected = PythonTestsProvider.test_matches(
                test.name, include, exclude)

            test_parameters_list = parameters.pop_raw(test.name)
            # If no parameters used, just create one empty set
            if test.selected and not test_parameters_list:
                test_parameters_list = [{}]

            if not isinstance(test_parameters_list, list):
                test_parameters_list = [test_parameters_list]

            for test_parameters in test_parameters_list:
                test.parameter_sets.append(test_parameters)

        parameters.ensure_consumed()
        config.ensure_consumed()
        return all_tests

    def find_python_tests(self):
        # Find all tests
        all_tests = []

        for _, module in inspect.getmembers(pluma.plugins, inspect.ismodule):
            for _, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, TestBase):
                    all_tests.append(TestDefinition(
                        name=f'{cls.__module__}.{cls.__name__}', testclass=cls, test_provider=self))

        return sorted(all_tests, key=attrgetter('name'))

    @staticmethod
    def test_matches(test_name: str, include: list, exclude: list) -> bool:
        # Very suboptimal way of doing it.
        for regex_string in exclude:
            regex = re.compile(regex_string)
            if re.match(regex, test_name):
                return False

        for regex_string in include:
            regex = re.compile(regex_string)
            if re.match(regex, test_name):
                return True

        return False
