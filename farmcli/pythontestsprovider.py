import testsuite
import re
import json
import inspect

from operator import attrgetter
from farmcore.baseclasses import Logger
from farmtest import TestBase
from farmcli import Configuration
from .config import TestDefinition, TestsProvider

log = Logger()


class PythonTestsProvider(TestsProvider):
    def __init__(self):
        pass

    def configuration_key(self):
        return 'core_tests'

    def all_tests(self, config):
        log.log('Core tests:', bold=True)
        if not config:
            log.log('    None\n')
            return []

        include = config.pop('include') or []
        exclude = config.pop('exclude') or []
        parameters = config.pop('parameters') or Configuration()
        all_tests = PythonTestsProvider.find_python_tests()

        # Instantiate tests selected
        for test in all_tests:
            test.selected = PythonTestsProvider.test_matches(
                test.name, include, exclude)

            check = 'x' if test.selected else ' '
            log.log(f'    [{check}] {test.name}',
                    color='green' if test.selected else 'normal')

            test_parameters_list = parameters.pop_raw(test.name)
            # If no parameters used, just create one empty set
            if test.selected and not test_parameters_list:
                test_parameters_list = [{}]

            if not isinstance(test_parameters_list, list):
                test_parameters_list = [test_parameters_list]

            for test_parameters in test_parameters_list:
                test.parameter_sets.append(test_parameters)

                if test.selected and len(test_parameters) > 0:
                    printed_data = None
                    if isinstance(test_parameters, Configuration):
                        printed_data = test_parameters
                    else:
                        printed_data = json.dumps(test_parameters)

                    log.log(f'          {printed_data}')

        log.log('')
        config.ensure_consumed()
        return all_tests

    @ staticmethod
    def find_python_tests():
        # Find all tests
        all_tests = []
        for m in inspect.getmembers(testsuite, inspect.isclass):
            if m[1].__module__.startswith(testsuite.__name__ + '.'):
                if issubclass(m[1], TestBase):
                    all_tests.append(TestDefinition(
                        name=f'{m[1].__module__}.{m[1].__name__}', testclass=m[1]))

        return sorted(all_tests, key=attrgetter('name'))

    @ staticmethod
    def test_matches(test_name, include, exclude):
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
