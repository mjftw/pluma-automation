import json
import os
from functools import partial

from farmcore.baseclasses import Logger, LogLevel
from farmtest import TestController, TestRunner
from farmtest.stock.deffuncs import sc_run_n_iterations
from farmcli import Configuration, ConfigurationError, TestsConfigError
from farmcore import Board

log = Logger()

SETTINGS_SECTION = 'settings'
PYTHON_TESTS_SECTION = 'tests'
SCRIPT_TESTS_SECTION = 'script_tests'
C_TESTS_SECTION = 'c_tests'


class TestsConfig:
    def __init__(self, config: Configuration, test_providers: list):
        if not config or not isinstance(config, Configuration):
            raise ValueError(
                f'Null or invalid \'config\', which must be of type \'{Configuration}\'')

        if not test_providers:
            raise ValueError('Null test providers passed')

        if not isinstance(test_providers, list):
            test_providers = [test_providers]

        self.settings_config = config.pop(SETTINGS_SECTION)
        self.test_providers = test_providers
        self.tests = None

        self.__populate_tests(config)

        config.ensure_consumed()

    def create_test_controller(self, board: Board):
        if not board or not isinstance(board, Board):
            raise ValueError(
                f'Null or invalid \'board\', which must be of type \'{Board}\'')

        try:
            settings = self.settings_config

            controller = TestController(
                testrunner=TestRunner(
                    board=board,
                    tests=TestsConfig.create_tests(
                        self.selected_tests(), board),
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

    def __populate_tests(self, tests_config):
        self.tests = []
        for test_provider in self.test_providers:
            provider_config = tests_config.pop(
                test_provider.configuration_key())
            self.tests.extend(test_provider.all_tests(provider_config))

    def selected_tests(self):
        return list(filter(lambda test: (test.selected), self.tests))

    def print_tests(self):
        TestsConfig.print_tests_definition(self.tests)

    @staticmethod
    def print_tests_definition(tests: list):
        tests = sorted(
            tests, key=lambda test: test.provider.configuration_key())

        last_provider = None
        for test in tests:
            if test.provider != last_provider:
                log.log(
                    f'{os.linesep}{test.provider.display_name()}:', bold=True)
                last_provider = test.provider

            check = 'x' if test.selected else ' '
            log.log(f'    [{check}] {test.name}',
                    color='green' if test.selected else 'normal')

            for test_parameters in test.parameter_sets:
                if test.selected and len(test_parameters) > 0:
                    printed_data = json.dumps(test_parameters)
                    log.log(f'          {printed_data}')

        log.log('')

    @staticmethod
    def create_tests(tests, board):
        test_objects = []
        for test in tests:
            try:
                for parameters in test.parameter_sets:
                    test_object = test.testclass(board, **parameters)
                    test_objects.append(test_object)
            except Exception as e:
                if f'{e}'.startswith('__init__()'):
                    raise TestsConfigError(
                        f'The test "{test.name}" requires one or more parameters to be provided '
                        f'in the "parameters" attribute in your "pluma.yml" file:\n    {e}')
                else:
                    raise TestsConfigError(
                        f'Failed to create test "{test.name}":\n    {e}')

        return test_objects
