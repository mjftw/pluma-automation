#!/usr/bin/env python3
import sys
import json
import time
import argparse

from farmcore import Board
from farmtest import TestController
from farmcli import Config, TestsConfig, TargetConfig, PlumaLogger

log = PlumaLogger()


def main():
    parser = argparse.ArgumentParser(
        description='A lightweight automated testing tool for embedded devices. Developed and maintained by Witekio, all rights reserved.')
    parser.add_argument('command', type=str, nargs='?', choices=['run', 'tests'], default='run',
                        help='command for pluma, defaults to "run"')

    tests_config_path = 'pluma.yml'
    target_config_path = 'pluma-target.yml'

    tests_config, target_config = Config.load_configuration(
        tests_config_path, target_config_path)

    args = parser.parse_args()
    if args.command == 'run':
        board = TargetConfig.create_board(target_config)

        default_log = 'pluma-{}.log'.format(time.strftime("%Y%m%d-%H%M%S"))
        board.log_file = tests_config.get('log') or default_log

        tests_controller = TestsConfig.create_test_controller(
            tests_config, board)
        tests_controller.run()

        print(tests_controller.get_test_results())

    elif args.command == 'tests':
        log.log(
            'List of core and script tests available, based on the current configuration.')
        TestsConfig.selected_tests(tests_config)


if __name__ == "__main__":
    main()
