import testsuite
import inspect
import re
import json

from functools import partial
from farmcore.baseclasses import Logger, LogLevel
from farmtest import TestController, TestBase, TestRunner, ShellTest, ExecutableTest
from farmtest.stock.deffuncs import sc_run_n_iterations
from farmcli import Configuration, ConfigurationError
from .testsbuilder import TestsBuilder

log = Logger()

SETTINGS_SECTION = 'settings'
PYTHON_TESTS_SECTION = 'tests'
SCRIPT_TESTS_SECTION = 'script_tests'
C_TESTS_SECTION = 'c_tests'


class TestsConfigError(Exception):
    pass


class TestDefinition():
    def __init__(self, name, testclass, parameters):
        self.name = name
        self.testclass = testclass
        self.parameters = parameters

        if not self.parameters:
            self.parameters = {}
        elif not isinstance(self.parameters, dict):
            raise ConfigurationError(
                f'Invalid parameters format for test "{name}": {self.parameters.__class__}, {self.parameters}')


class TestsConfig:
    @staticmethod
    def create_test_controller(config, board):
        try:
            settings = config.pop(SETTINGS_SECTION)
            tests = TestsConfig.selected_tests_from_config(config)
            config.ensure_consumed()

            test_objects = TestsConfig.create_tests(tests, board)

            controller = TestController(
                testrunner=TestRunner(
                    board=board,
                    tests=test_objects,
                    sequential=settings.pop('sequential', default=True),
                    email_on_fail=settings.pop('email_on_fail', default=False),
                    continue_on_fail=settings.pop(
                        'continue_on_fail',  default=True),
                    skip_tasks=settings.pop('skip_tasks',  default=[]),
                    use_testcore=settings.pop(
                        'board_test_sequence', default=False)
                ),
                log_func=partial(log.log, level=LogLevel.INFO),
                verbose_log_func=partial(log.log, level=LogLevel.NOTICE)
            )

            iterations = settings.pop('iterations')
            if iterations:
                controller.run_condition = sc_run_n_iterations(int(iterations))

            settings.ensure_consumed()
        except ConfigurationError as e:
            raise TestsConfigError(e)

        return controller

    @staticmethod
    def find_python_tests():
        # Find all tests
        all_tests = {}
        for m in inspect.getmembers(testsuite, inspect.isclass):
            if m[1].__module__.startswith(testsuite.__name__ + '.'):
                if issubclass(m[1], TestBase):
                    # Dictionary with the class name as key, and class as value
                    all_tests[f'{m[1].__module__}.{m[1].__name__}'] = m[1]

        return all_tests

    @staticmethod
    def print_tests(config):
        TestsConfig.selected_tests_from_config(config)

    @staticmethod
    def selected_tests_from_config(config):
        return TestsConfig.selected_tests(config.pop(PYTHON_TESTS_SECTION),
                                          config.pop(SCRIPT_TESTS_SECTION),
                                          config.pop(C_TESTS_SECTION))

    @staticmethod
    def selected_tests(python_tests_config, script_tests_config, c_tests_config):
        tests = []
        tests.extend(TestsConfig.selected_python_tests(python_tests_config))
        tests.extend(TestsConfig.selected_script_tests(script_tests_config))
        tests.extend(TestsConfig.selected_c_tests(c_tests_config))
        return tests

    @staticmethod
    def selected_python_tests(config):
        log.log('Core tests:', bold=True)
        if not config:
            log.log('    None\n')
            return []

        include = config.pop('include') or []
        exclude = config.pop('exclude') or []
        parameters = config.pop('parameters') or Configuration()

        all_tests = TestsConfig.find_python_tests()

        # Instantiate tests selected
        selected_tests = []
        for test_name in sorted(all_tests):
            selected = TestsConfig.test_matches(test_name, include, exclude)
            test_parameters_list = parameters.pop_raw(test_name)
            check = 'x' if selected else ' '
            log.log(f'    [{check}] {test_name}',
                    color='green' if selected else 'normal')

            if selected:
                if not isinstance(test_parameters_list, list):
                    test_parameters_list = [test_parameters_list]

                for test_parameters in test_parameters_list:
                    if test_parameters:
                        printed_data = None
                        if isinstance(test_parameters, Configuration):
                            printed_data = test_parameters
                        else:
                            printed_data = json.dumps(test_parameters)

                        log.log(f'          {printed_data}')

                    test = TestDefinition(
                        test_name, testclass=all_tests[test_name],
                        parameters=test_parameters)
                    selected_tests.append(test)

        log.log('')
        config.ensure_consumed()
        parameters.ensure_consumed()
        return selected_tests

    @staticmethod
    def selected_script_tests(config):
        log.log('Inline tests (pluma.yml):', bold=True)
        if not config:
            log.log('    None\n')
            return []

        if isinstance(config, Configuration):
            config = config.content()

        selected_tests = []
        for test_name in config:
            log.log(f'    [x] {test_name}', color='green')

            try:
                test_parameters = config[test_name]
                test_parameters['name'] = test_name
                test = TestDefinition(
                    test_name, testclass=ShellTest, parameters=test_parameters)
                selected_tests.append(test)
            except Exception as e:
                raise TestsConfigError(
                    f'Failed to parse script test "{test_name}":\n    {e}')

        log.log('')
        return selected_tests

    @staticmethod
    def selected_c_tests(config):
        log.log('C tests:', bold=True)
        if not config:
            log.log('    None\n')
            return []

        yocto_sdk_file = config.pop('yocto_sdk')
        env_file = config.pop('source_environment')
        if not yocto_sdk_file and not env_file:
            raise TestsConfigError(
                'Missing "yocto_sdk" or "source_environment" attributes for C tests')

        install_dir = None
        if yocto_sdk_file:
            install_dir = TestsBuilder.install_yocto_sdk(yocto_sdk_file)

        if not env_file:
            env_file = TestsBuilder.find_yocto_sdk_env_file(install_dir)

        selected_tests = []
        tests_config = config.pop('tests', default={}).content()
        for test_name in tests_config:
            log.log(f'    [x] {test_name}', color='green')

            try:
                test_parameters = tests_config[test_name]
                test_executable = TestsBuilder.build_c_test(
                    target_name=test_name, env_file=env_file,
                    sources=test_parameters.pop('sources'), flags=test_parameters.pop('flags', None))

                test_parameters['executable_file'] = test_executable

                test = TestDefinition(
                    test_name, testclass=ExecutableTest, parameters=test_parameters)
                selected_tests.append(test)
            except KeyError as e:
                raise TestsConfigError(
                    f'Error processing C test "{test_name}": Missing mandatory attribute {e}')
            except Exception as e:
                raise TestsConfigError(
                    f'Error processing C test "{test_name}": {e}')

        return selected_tests

    @staticmethod
    def create_tests(tests, board):
        test_objects = []
        for test in tests:
            test_name = test.name
            try:
                test_object = test.testclass(board, **test.parameters)
                test_objects.append(test_object)
            except Exception as e:
                if f'{e}'.startswith('__init__()'):
                    raise TestsConfigError(
                        f'The test "{test_name}" requires one or more parameters to be provided '
                        f'in the "parameters" attribute in your "pluma.yml" file:\n    {e}')
                else:
                    raise TestsConfigError(
                        f'Failed to create test "{test_name}":\n    {e}')

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
