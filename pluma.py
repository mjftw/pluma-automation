#!/usr/bin/env python3
import sys
import json
import time
import argparse
import traceback
import os

from farmcore import Board
from farmcore.baseclasses import Logger, LogMode, LogLevel
from farmtest import TestController
from farmcli import PlumaConfig, TestsConfig, TargetConfig, TestsBuilder
from farmcli import TestsConfigError, TargetConfigError, TestsBuildError

log = Logger()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='A lightweight automated testing tool for embedded devices.')
    parser.add_argument('command', type=str, nargs='?', choices=['run', 'check', 'tests', 'clean'], default='run',
                        help='command for pluma, defaults to "run". "run": Run the tests suite, '
                        '"check": validate configuration files and tests, '
                        '"tests": list all tests available and selected, '
                        '"clean": remove logs, toolchains, and built executables')
    parser.add_argument(
        '-v', '--verbose', action='store_const', const=True, help='prints more information related to tests and progress')
    parser.add_argument(
        '-q', '--quiet', action='store_const', const=True, help='print only test progress and results')
    parser.add_argument(
        '-c', '--config', default='pluma.yml', help='path to the tests configuration file. Default: "pluma.yml"')
    parser.add_argument(
        '-t', '--target', default='pluma-target.yml', help='path to the taret configuration file. Default: "pluma-target.yml"')
    parser.add_argument(
        '-f', '--force', action='store_const', const=True, help='force operation instead of prompting')
    parser.add_argument(
        '--silent', action='store_const', const=True, help='silence all output')
    parser.add_argument(
        '--debug', action='store_const', const=True, help='enable debug information')

    args = parser.parse_args()
    return args


def instantiate(args, tests_config_path, target_config_path):
    tests_config, target_config = PlumaConfig.load_configuration(
        tests_config_path, target_config_path)

    board = TargetConfig.create_board(target_config)
    default_log = 'pluma-{}.log'.format(time.strftime("%Y%m%d-%H%M%S"))
    board.log_file = tests_config.pop('log') or default_log

    return TestsConfig.create_test_controller(
        tests_config, board)


def execute_run(args, tests_config_path, target_config_path):
    controller = instantiate(args, tests_config_path, target_config_path)

    success = controller.run()
    if success:
        log.log('All tests were successful.',
                level=LogLevel.IMPORTANT, color='green', bold=True)
    else:
        log.log('One of more test failed.',
                level=LogLevel.IMPORTANT, color='red', bold=True)

    return success


def execute_check(args, tests_config_path, target_config_path):
    instantiate(args, tests_config_path, target_config_path)
    log.log('Configuration and tests successfully validated.',
            level=LogLevel.IMPORTANT)


def execute_tests(args, tests_config_path, target_config_path):
    tests_config, _ = PlumaConfig.load_configuration(
        tests_config_path, target_config_path)

    log.log(
        'List of core and script tests available, based on the current configuration.')
    TestsConfig.print_tests(tests_config)


def execute_clean(args):
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
        if args.command == 'run':
            success = execute_run(args, tests_config_path, target_config_path)
            exit(0 if success else 1)
        elif args.command == 'check':
            # Force log mode to print the relevant information
            mode_set = log.mode
            log.mode = LogMode.VERBOSE
            execute_check(args, tests_config_path, target_config_path)
            log.mode = mode_set
        elif args.command == 'tests':
            # Force log mode to print the relevant information
            mode_set = log.mode
            log.mode = LogMode.VERBOSE
            execute_tests(args, tests_config_path, target_config_path)
            log.mode = mode_set
        elif args.command == 'clean':
            execute_clean(args)
    except TestsConfigError as e:
        log.error(
            f'Error while parsing the tests configuration ({tests_config_path}):\n  {e}')
        exit(-2)
    except TargetConfigError as e:
        log.error(
            f'Error while parsing the target configuration ({target_config_path}):\n  {e}')
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
