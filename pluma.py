#!/usr/bin/env python3
import sys
import json
import time
import argparse

from farmcore import Board
from farmtest import TestController
from farmcli import PlumaConfig, TestsConfig, TargetConfig, PlumaLogger

log = PlumaLogger.logger()


def main():
    parser = argparse.ArgumentParser(
        description='A lightweight automated testing tool for embedded devices. Developed and maintained by Witekio, all rights reserved.')
    parser.add_argument('command', type=str, nargs='?', choices=['run', 'tests'], default='run',
                        help='command for pluma, defaults to "run"')
    parser.add_argument(
        '-q', '--quiet', action='store_const', const=True, help='hide context information, such has components and tests list')
    parser.add_argument(
        '-c', '--config', default='pluma.yml', help='path to the tests configuration file. Default: "pluma.yml"')
    parser.add_argument(
        '-t', '--target', default='pluma-target.yml', help='path to the taret configuration file. Default: "pluma-target.yml"')

    args = parser.parse_args()
    tests_config_path = args.config
    target_config_path = args.target

    if args.command == 'run':
        if args.quiet:
            log.enabled = False

        tests_config, target_config = PlumaConfig.load_configuration(
            tests_config_path, target_config_path)

        board = TargetConfig.create_board(target_config)

        default_log = 'pluma-{}.log'.format(time.strftime("%Y%m%d-%H%M%S"))
        board.log_file = tests_config.take('log') or default_log

        tests_controller = TestsConfig.create_test_controller(
            tests_config, board)
        tests_controller.run()

        print(tests_controller.get_test_results())

    elif args.command == 'tests':
        tests_config, _ = PlumaConfig.load_configuration(
            tests_config_path, target_config_path)

        log.log(
            'List of core and script tests available, based on the current configuration.')
        TestsConfig.print_tests(tests_config)


if __name__ == "__main__":
    main()
