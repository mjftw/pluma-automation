#!/usr/bin/env python3
import sys
import json
import time
import argparse

from farmcore import Board
from farmtest import TestController
from farmcli import PlumaConfig, TestsConfig, TargetConfig, PlumaLogger, TestsConfigError, TargetConfigError

log = PlumaLogger.logger()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='A lightweight automated testing tool for embedded devices.')
    parser.add_argument('command', type=str, nargs='?', choices=['run', 'tests'], default='run',
                        help='command for pluma, defaults to "run"')
    parser.add_argument(
        '-q', '--quiet', action='store_const', const=True, help='hide context information, such has components and tests list')
    parser.add_argument(
        '-c', '--config', default='pluma.yml', help='path to the tests configuration file. Default: "pluma.yml"')
    parser.add_argument(
        '-t', '--target', default='pluma-target.yml', help='path to the taret configuration file. Default: "pluma-target.yml"')
    parser.add_argument(
        '--debug', action='store_const', const=True, help='enable debug information')

    args = parser.parse_args()
    return args


def execute_run(args, tests_config_path, target_config_path):
    if args.quiet:
        log.enabled = False
    elif args.debug:
        log.debug_enabled = True

    tests_config, target_config = PlumaConfig.load_configuration(
        tests_config_path, target_config_path)

    board = TargetConfig.create_board(target_config)

    default_log = 'pluma-{}.log'.format(time.strftime("%Y%m%d-%H%M%S"))
    board.log_file = tests_config.pop('log') or default_log

    tests_controller = TestsConfig.create_test_controller(
        tests_config, board)
    success = tests_controller.run()

    print(tests_controller.get_test_results())

    return success


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
