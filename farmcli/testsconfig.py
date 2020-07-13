import tests
import logging
import inspect
import re
import json

from farmtest import TestController, TestBase, TestRunner, ShellTest
from farmtest.stock.deffuncs import sc_run_n_iterations
from farmcli import PlumaLogger, Configuration

log = PlumaLogger.logger()

SETTINGS_SECTION = 'settings'
PYTHON_TESTS_SECTION = 'tests'
SCRIPT_TESTS_SECTION = 'script_tests'


class TestsConfig:
    @staticmethod
    def create_test_controller(config, board):
        settings = config.take(SETTINGS_SECTION)
        tests = TestsConfig.selected_tests(
            config.take(PYTHON_TESTS_SECTION), config.take(SCRIPT_TESTS_SECTION))
        config.ensure_consumed()

        test_objects = TestsConfig.create_tests(tests, board)

        controller = TestController(
            testrunner=TestRunner(
                board=board,
                tests=test_objects,
                sequential=settings.take('sequential') if settings.take(
                    'sequential') != None else True,
                email_on_fail=settings.take('email_on_fail') or False,
                continue_on_fail=settings.take('continue_on_fail') or True,
                skip_tasks=settings.take('skip_tasks') or [],
            )
        )

        iterations = settings.take('iterations')
        if iterations:
            controller.run_condition = sc_run_n_iterations(int(iterations))

        settings.ensure_consumed()

        return controller

    @staticmethod
    def find_python_tests():
        # Find all tests
        all_tests = {}
        for m in inspect.getmembers(tests, inspect.isclass):
            if m[1].__module__.startswith(tests.__name__ + '.'):
                # Dictionary with the class name as key, and class as value
                all_tests[f'{m[1].__module__}.{m[1].__name__}'] = m[1]

        return all_tests

    @staticmethod
    def print_tests(config):
        TestsConfig.selected_tests(config.take(PYTHON_TESTS_SECTION),
                                   config.take(SCRIPT_TESTS_SECTION))

    @staticmethod
    def selected_tests(python_tests_config, script_tests_config):
        if not python_tests_config:
            log.error(
                f'Configuration file is invalid, missing a "{PYTHON_TESTS_SECTION}" section')
            exit(-2)

        tests = TestsConfig.selected_python_tests(python_tests_config)
        tests.extend(TestsConfig.selected_script_tests(
            script_tests_config.content()))
        return tests

    @staticmethod
    def selected_python_tests(config):
        if not config:
            raise ValueError('Null configuration provided')

        include = config.take('include') or []
        exclude = config.take('exclude') or []
        parameters = config.take('parameters') or Configuration()

        all_tests = TestsConfig.find_python_tests()

        # Instantiate tests selected
        selected_tests = []
        log.log('Core tests:', bold=True)
        for test_name in sorted(all_tests):
            selected = TestsConfig.test_matches(test_name, include, exclude)
            test_parameters_list = parameters.take_raw(test_name)
            check = 'x' if selected else ' '
            log.log(f'    [{check}] {test_name}',
                    color='green' if selected else 'normal')

            if selected:
                if not isinstance(test_parameters_list, list):
                    test_parameters_list = [test_parameters_list]

                for test_parameters in test_parameters_list:
                    if test_parameters:
                        json_data = None
                        if isinstance(test_parameters, Configuration):
                            json_data = test_parameters
                        else:
                            json_data = json.dumps(test_parameters)

                        log.log(f'          {json_data}')

                    selected_tests.append(
                        {'name': test_name, 'class': all_tests[test_name], 'parameters': test_parameters})

        log.log('')
        config.ensure_consumed()
        return selected_tests

    @staticmethod
    def selected_script_tests(config):
        log.log('Inline tests (pluma.yml):', bold=True)
        if not config:
            log.log('    None\n')
            return []

        selected_tests = []
        for test_name in config:
            log.log(f'    [x] {test_name}', color='green')

            try:
                test_parameters = config[test_name]
                test_parameters['name'] = test_name
                test = {'name': test_name, 'class': ShellTest,
                        'parameters': test_parameters}
                selected_tests.append(test)
            except Exception as e:
                log.error(
                    f'Failed to parse script test "{test_name}":\n    {e}')
                exit(-2)

        log.log('')
        return selected_tests

    @staticmethod
    def create_tests(tests, board):
        test_objects = []
        for test in tests:
            test_name = test['name']
            try:
                test_object = test['class'](board, test['parameters'])
                test_objects.append(test_object)
            except Exception as e:
                log.error(f'Failed to create test "{test_name}":\n    {e}')
                exit(-3)

        return test_objects

    @staticmethod
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
