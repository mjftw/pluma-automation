import tests
import logging
import yaml
import inspect
import re
import json

from farmtest import TestController, TestBase, TestRunner, ShellTest
from farmtest.stock.deffuncs import sc_run_n_iterations
from farmcli import PlumaLogger

log = PlumaLogger.logger()


class Config:
    @staticmethod
    def load_configuration(tests_config_path, target_config_path):
        tests_config = None
        target_config = None

        try:
            with open(tests_config_path, 'r') as config:
                tests_config = yaml.load(config, Loader=yaml.FullLoader)
        except FileNotFoundError:
            log.error('Configuration file "' + tests_config_path +
                      '" not found in the current folder')
            exit(-1)
        except:
            log.error(
                f'Failed to open configuration file "{tests_config_path}"')
            exit(-1)

        try:
            with open(target_config_path, 'r') as config:
                target_config = yaml.load(config, Loader=yaml.FullLoader)
        except FileNotFoundError:
            log.error('Configuration file "' + target_config_path +
                      '" not found in the current folder')
            exit(-1)
        except:
            log.error(
                f'Failed to open configuration file "{target_config_path}"')
            exit(-1)

        return tests_config, target_config


class TestsConfig:
    @staticmethod
    def create_test_controller(config, board):
        tests = TestsConfig.create_tests(config.get('tests'), board)
        tests.extend(TestsConfig.create_script_tests(
            config.get('script_tests'), board))

        controller = TestController(
            testrunner=TestRunner(
                board=board,
                tests=tests,
                sequential=config.get('sequential') or True,
                email_on_fail=config.get('email_on_fail') or False,
                continue_on_fail=config.get('continue_on_fail') or True,
                skip_tasks=config.get('skip_tasks') or [],
            )
        )

        iterations = config.get('iterations')
        if iterations:
            controller.run_condition = sc_run_n_iterations(int(iterations))

        return controller

    @ staticmethod
    def find_tests():
        # Find all tests
        all_tests = {}
        for m in inspect.getmembers(tests, inspect.isclass):
            if m[1].__module__.startswith(tests.__name__ + '.'):
                # Dictionary with the class name as key, and class as value
                all_tests[f'{m[1].__module__}.{m[1].__name__}'] = m[1]

        return all_tests

    @ staticmethod
    def create_tests(config, board):
        include = config.get('include') or []
        exclude = config.get('exclude') or []
        parameters = config.get('parameters') or {}

        all_tests = TestsConfig.find_tests()

        # Instantiate tests selected
        test_objects = []
        log.log('\nCore tests:', bold=True)
        for test_name in sorted(all_tests):
            selected = TestsConfig.test_matches(test_name, include, exclude)
            test_parameters_list = parameters.get(test_name)
            check = 'x' if selected else ' '
            log.log(f'    [{check}] {test_name}',
                    color='green' if selected else 'normal')

            if selected:
                if not isinstance(test_parameters_list, list):
                    test_parameters_list = [test_parameters_list]

                for test_parameters in test_parameters_list:
                    if test_parameters:
                        log.log(f'          {json.dumps(test_parameters)}')

                    test_objects.append(
                        all_tests[test_name](board, test_parameters))

        return test_objects

    @ staticmethod
    def create_script_tests(config, board):
        log.log('\nInline tests (pluma.yml):', bold=True)
        if not config:
            log.log('    None\n')
            return []

        test_objects = []
        for test_name in config:
            log.log(f'    [x] {test_name}', color='green')

            try:
                test_parameters = config[test_name]
                test_parameters['name'] = test_name
            except:
                raise ValueError(
                    f'Failed to create script test "{test_name}"')

            test = ShellTest(board, test_parameters)
            test_objects.append(test)

        log.log('')
        return test_objects

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
