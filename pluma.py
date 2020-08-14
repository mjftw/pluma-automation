#!/usr/bin/env python3
import sys
import time
import argparse
import traceback
import os

from farmcore.baseclasses import Logger, LogMode, LogLevel
from farmtest import TestController
from farmcli import PlumaConfig, TestsConfig, TestsBuilder, TargetConfig
from farmcli import TestsConfigError, TestsBuildError, TargetConfigError
from farmcli import PythonTestsProvider, ShellTestsProvider, CTestsProvider, DeviceActionProvider
from version import get_farmcore_version

log = Logger()

RUN_COMMAND = 'run'
CHECK_COMMAND = 'check'
TESTS_COMMAND = 'tests'
CLEAN_COMMAND = 'clean'
VERSION_COMMAND = 'version'
COMMANDS = [RUN_COMMAND, CHECK_COMMAND,
            TESTS_COMMAND, CLEAN_COMMAND, VERSION_COMMAND]


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='A lightweight automated testing tool for embedded devices.')
    parser.add_argument('command', type=str, nargs='?', choices=COMMANDS, default=RUN_COMMAND,
                        help=f'command for pluma, defaults to "{RUN_COMMAND}". "{RUN_COMMAND}": Run the tests suite, '
                        f'"{CHECK_COMMAND}": validate configuration files and tests, '
                        f'"{TESTS_COMMAND}": list all tests available and selected, '
                        f'"{CLEAN_COMMAND}": remove logs, toolchains, and built executables')
    parser.add_argument(
        '-v', '--verbose', action='store_const', const=True, help='prints more information related to tests and progress')
    parser.add_argument(
        '-q', '--quiet', action='store_const', const=True, help='print only test progress and results')
    parser.add_argument(
        '-c', '--config', default='pluma.yml', help='path to the tests configuration file. Default: "pluma.yml"')
    parser.add_argument(
        '-t', '--target', default='pluma-target.yml', help='path to the target configuration file. Default: "pluma-target.yml"')
    parser.add_argument(
        '-f', '--force', action='store_const', const=True, help='force operation instead of prompting')
    parser.add_argument(
        '--silent', action='store_const', const=True, help='silence all output')
    parser.add_argument(
        '--debug', action='store_const', const=True, help='enable debug information')

    args = parser.parse_args()
    return args


def tests_providers():
    return [PythonTestsProvider(), ShellTestsProvider(),
            CTestsProvider(), DeviceActionProvider()]


def instantiate(args, tests_config_path: str, target_config_path: str, show_tests_list: bool) -> TestController:
    tests_config, target_config = PlumaConfig.load_configurations(
        tests_config_path, target_config_path)

    board = TargetConfig.create_board(target_config)
    default_log = 'pluma-{}.log'.format(time.strftime("%Y%m%d-%H%M%S"))
    board.log_file = tests_config.pop('log') or default_log

    testsConfig = TestsConfig(tests_config, tests_providers())

    tests_list_log_level = LogLevel.INFO if show_tests_list else LogLevel.NOTICE
    testsConfig.print_tests(tests_list_log_level)

    return testsConfig.create_test_controller(board)


def execute_run(args, tests_config_path: str, target_config_path: str, check_only: bool = False):
    '''Execute the "run" command, and allow checking only ("check" command).'''
    controller = instantiate(args, tests_config_path,
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


def execute_tests(args, tests_config_path: str, target_config_path: str):
    '''Execute the "tests" command, listing all tests.'''
    tests_config, _ = PlumaConfig.load_configurations(
        tests_config_path, target_config_path)

    log.log(
        'List of core and script tests available, based on the current configuration.')
    testsConfig = TestsConfig(tests_config, tests_providers())
    testsConfig.print_tests(log_level=LogLevel.IMPORTANT)


def execute_clean(args):
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

    TestsBuilder.clean(args.force)


def main():
    args = parse_arguments()

    if args.silent:
        log.mode = LogMode.SILENT
    elif args.debug:
        log.mode = LogMode.DEBUG
    elif args.quiet:
        log.mode = LogMode.QUIET
    elif args.verbose:
        log.mode = LogMode.VERBOSE
    else:
        log.mode = LogMode.NORMAL

    tests_config_path = args.config
    target_config_path = args.target

    try:
        command = args.command
        if command == RUN_COMMAND:
            success = execute_run(args, tests_config_path, target_config_path)
            exit(0 if success else 1)
        elif args.command == CHECK_COMMAND:
            execute_run(args, tests_config_path, target_config_path,
                        check_only=True)
        elif args.command == TESTS_COMMAND:
            execute_tests(args, tests_config_path, target_config_path)
        elif args.command == CLEAN_COMMAND:
            execute_clean(args)
        elif command == VERSION_COMMAND:
            log.log(get_farmcore_version(), level=LogLevel.IMPORTANT)
    except TestsConfigError as e:
        log.error(
            f'Error while parsing the tests configuration ({tests_config_path}):{os.linesep}  {e}')
        exit(-2)
    except TargetConfigError as e:
        log.error(
            f'Error while parsing the target configuration ({target_config_path}):{os.linesep}  {e}')
        exit(-3)
    except TestsBuildError as e:
        log.error(
            f'Error while building tests:\n  {e}')
        exit(-4)
    except Exception as e:
        if log.mode in [LogMode.VERBOSE, LogMode.DEBUG]:
            traceback.print_exc()
        log.error(e)
        exit(-1)


if __name__ == "__main__":
    main()
