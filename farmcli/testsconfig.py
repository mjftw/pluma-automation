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
    def __init__(self, config):
        self.config = config

    @staticmethod
    def create_test_controller(config, board, tests_providers):
        if not config or not isinstance(config, Configuration):
            raise ValueError(
                f'Null or invalid \'config\', which must be of type \'{Configuration}\'')
        if not board or not isinstance(board, Board):
            raise ValueError(
                f'Null or invalid \'board\', which must be of type \'{Board}\'')
        if not tests_providers:
            raise ValueError('Tests providers list must be set')

        try:
            settings = config.pop(SETTINGS_SECTION)
            tests = TestsConfig.selected_tests(config, tests_providers)
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
    def selected_tests(config, tests_providers):
        selected_tests = []
        for test_provider in tests_providers:
            provider_config = config.pop(test_provider.configuration_key())
            selected_tests.extend(
                test_provider.selected_tests(provider_config))

        return selected_tests

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
