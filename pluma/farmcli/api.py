import sys
import time
import os

from farmcore.baseclasses import Logger, LogLevel
from farmtest import TestController
from farmcli import PlumaConfig, TestsConfig, TestsBuilder, TargetConfig
from farmcli import TestsBuildError
from farmcli import PythonTestsProvider, ShellTestsProvider, CTestsProvider, DeviceActionProvider
from version import get_farmcore_version

log = Logger()


class Pluma:
    '''Top level API class for Pluma'''
    @staticmethod
    def tests_providers() -> list:
        return [PythonTestsProvider(), ShellTestsProvider(),
                CTestsProvider(), DeviceActionProvider()]

    @staticmethod
    def execute_run(tests_config_path: str, target_config_path: str, check_only: bool = False) -> bool:
        '''Execute the "run" command, and allow checking only ("check" command).'''
        controller = Pluma.build_test_controller(tests_config_path,
                                                 target_config_path, show_tests_list=check_only)
        if check_only:
            log.log('Configuration and tests successfully validated.',
                    level=LogLevel.IMPORTANT)
            return True

        success = controller.run()
        if success:
            log.log('All tests were successful.',
                    level=LogLevel.IMPORTANT, color='green', bold=True)
        else:
            log.log('One of more test failed.',
                    level=LogLevel.IMPORTANT, color='red', bold=True)

        return success

    @staticmethod
    def execute_tests(tests_config_path: str, target_config_path: str):
        '''Execute the "tests" command, listing all tests.'''
        tests_config, _ = PlumaConfig.load_configurations(
            tests_config_path, target_config_path)

        log.log(
            'List of core and script tests available, based on the current configuration.')
        testsConfig = TestsConfig(tests_config, Pluma.tests_providers())
        testsConfig.print_tests(log_level=LogLevel.IMPORTANT)

    @staticmethod
    def execute_clean(force: bool = False):
        '''Execute the "clean" command.'''
        log.log('Removing log files...')
        try:
            logs_folder = os.path.dirname(
                os.path.abspath(sys.modules['__main__'].__file__))

            for file in os.listdir(logs_folder):
                if file.endswith('.log'):
                    os.remove(f'{logs_folder}/{file}')
        except Exception as e:
            raise TestsBuildError(
                f'Failed to remove log files: {e}')

        TestsBuilder.clean(force)

    @staticmethod
    def build_test_controller(tests_config_path: str, target_config_path: str, show_tests_list: bool) -> TestController:
        tests_config, target_config = PlumaConfig.load_configurations(
            tests_config_path, target_config_path)

        board = TargetConfig.create_board(target_config)
        default_log = 'pluma-{}.log'.format(time.strftime("%Y%m%d-%H%M%S"))
        board.log_file = tests_config.pop('log') or default_log

        testsConfig = TestsConfig(tests_config, Pluma.tests_providers())

        tests_list_log_level = LogLevel.INFO if show_tests_list else LogLevel.NOTICE
        testsConfig.print_tests(tests_list_log_level)

        return testsConfig.create_test_controller(board)

    @staticmethod
    def version() -> str:
        '''Return the version string of Pluma'''
        return get_farmcore_version()
