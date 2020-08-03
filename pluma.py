#!/usr/bin/env python3
import sys
import json
import time
import argparse

from farmcore import Board
from farmcore.baseclasses import Logger, LogMode
from farmtest import TestController
from farmcli import PlumaConfig, TestsConfig, TargetConfig, TestsConfigError, TargetConfigError

log = Logger()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='A lightweight automated testing tool for embedded devices.')
    parser.add_argument('command', type=str, nargs='?', choices=['run', 'check', 'tests'], default='run',
                        help='command for pluma, defaults to "run". "run": Run the tests suite, "check": validate configuration files and tests, "tests": list all tests available and selected')
    parser.add_argument(
        '-v', '--verbose', action='store_const', const=True, help='prints more information related to tests and progress')
    parser.add_argument(
        '-q', '--quiet', action='store_const', const=True, help='print only test progress and results')
    parser.add_argument(
        '-c', '--config', default='pluma.yml', help='path to the tests configuration file. Default: "pluma.yml"')
    parser.add_argument(
        '-t', '--target', default='pluma-target.yml', help='path to the taret configuration file. Default: "pluma-target.yml"')
    parser.add_argument(
        '--silent', action='store_const', const=True, help='silence all output')
    parser.add_argument(
        '--debug', action='store_const', const=True, help='enable debug information')

    args = parser.parse_args()
    return args


def instantiate(args, tests_config_path, target_config_path):
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

    return success


def execute_check(args, tests_config_path, target_config_path):
    instantiate(args, tests_config_path, target_config_path)
    log.log('Configuration and tests successfully validated.')


def execute_tests(args, tests_config_path, target_config_path):
    tests_config, _ = PlumaConfig.load_configuration(
        tests_config_path, target_config_path)

    log.log(
        'List of core and script tests available, based on the current configuration.')
    TestsConfig.print_tests(tests_config)


def main():
    args = parse_arguments()
    tests_config_path = args.config
    target_config_path = args.target

    try:
        if args.command == 'run':
            success = execute_run(args, tests_config_path, target_config_path)
            exit(0 if success else 1)
        elif args.command == 'check':
            execute_check(args, tests_config_path, target_config_path)
        elif args.command == 'tests':
            execute_tests(args, tests_config_path, target_config_path)
    except TestsConfigError as e:
        log.error(
            f'Error while parsing the tests configuration ({tests_config_path}):\n  {e}')
        exit(-1)
    except TargetConfigError as e:
        log.error(
            f'Error while parsing the target configuration ({target_config_path}):\n  {e}')
        exit(-2)


if __name__ == "__main__":
    main()
