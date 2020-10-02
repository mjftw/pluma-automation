import inspect
from typing import List
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

        includes = config.pop('include') or []
        excludes = config.pop('exclude') or []
        parameters = config.pop('parameters') or Configuration()
        all_tests = self.find_python_tests()

        PythonTestsProvider.validate_match_strings(all_tests,
                                                   includes+excludes)

        # Instantiate tests selected
        for test in all_tests:
            test.selected = PythonTestsProvider.test_selected(test.name,
                                                              includes, excludes)

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
        '''Search plugins module for classes inheriting TestBase and create TestDefinitions'''

        modules = {module_name: module
                   for module_name, module in inspect.getmembers(pluma.plugins, inspect.ismodule)}
        submodules = {submodule_name: submodule
                      for module in modules.values()
                      for submodule_name, submodule in inspect.getmembers(module, inspect.ismodule)}

        test_classes = {}
        for module_name, module in {**modules, **submodules}.items():
            for class_name, cls in inspect.getmembers(module, inspect.isclass):
                # Exclude TestBase classes imported in but not defined in module
                if issubclass(cls, TestBase) and cls.__module__.startswith(module.__name__):
                    full_name = f'{cls.__module__[cls.__module__.index(module_name):]}.{class_name}'
                    test_classes[full_name] = cls

        all_tests = [TestDefinition(name=class_name, testclass=cls, test_provider=self)
                     for class_name, cls in test_classes.items()]

        return sorted(all_tests, key=attrgetter('name'))

    @staticmethod
    def test_selected(test_name: str, includes: List[str], excludes: List[str]) -> bool:
        for exclude in excludes:
            if PythonTestsProvider.test_match(test_name, match_string=exclude):
                return False

        for include in includes:
            if PythonTestsProvider.test_match(test_name, match_string=include):
                return True

        return False

    @staticmethod
    def test_match(test_name: str, match_string: str):
        test_name_list = test_name.split('.')
        match_string_list = match_string.split('.')

        return all(name == match for name, match in
                   zip(test_name_list, match_string_list))

    @staticmethod
    def validate_match_strings(all_tests: List[TestDefinition], match_strings: List[str]):
        '''Error if any match_string matches no test'''
        not_matched = match_strings
        for test in all_tests:
            for match_string in match_strings:
                if PythonTestsProvider.test_match(test.name, match_string):
                    not_matched.remove(match_string)

        if not_matched:
            raise ValueError(f'Some include/exclude rules matched no tests: {not_matched}')
