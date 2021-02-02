import argparse
import traceback
import os
from typing import Any, Callable, Optional

from pluma.core.baseclasses import Logger, LogMode, LogLevel
from pluma.core.builder import TestsBuildError
from pluma.cli import Pluma, TestsConfigError, TargetConfigError
from pluma.cli.plugins import load_plugin_modules

log = Logger()

RUN_COMMAND = 'run'
CHECK_COMMAND = 'check'
TESTS_COMMAND = 'tests'
CLEAN_COMMAND = 'clean'
VERSION_COMMAND = 'version'
COMMANDS = [RUN_COMMAND, CHECK_COMMAND,
            TESTS_COMMAND, CLEAN_COMMAND, VERSION_COMMAND]


def arg_is_x(arg: Any, predicate: Callable, err_msg: Optional[str] = None):
    if not predicate(arg):
        raise argparse.ArgumentTypeError(err_msg or "")

    return arg


def arg_is_file(path, info=None):
    return arg_is_x(path, os.path.isfile, f'{f"{info} " or ""}file does not exist: {path}')


def arg_is_dir(path, info=None):
    return arg_is_x(path, os.path.isdir, f'{f"{info} " or ""}directory does not exist: {path}')


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='A lightweight automated testing tool for embedded devices.')
    parser.add_argument('command', type=str, nargs='?', choices=COMMANDS, default=RUN_COMMAND,
                        help=f'command for pluma, defaults to "{RUN_COMMAND}". "{RUN_COMMAND}": Run the tests suite, '
                        f'"{CHECK_COMMAND}": validate configuration files and tests, '
                        f'"{TESTS_COMMAND}": list all tests available and selected, '
                        f'"{CLEAN_COMMAND}": remove logs, toolchains, and built executables')
    parser.add_argument(
        '-v', '--verbose', action='store_const', const=True,
        help='prints more information related to tests and progress')
    parser.add_argument(
        '-q', '--quiet', action='store_const', const=True,
        help='print only test progress and results')
    parser.add_argument(
        '-c', '--config', default='pluma.yml',
        type=lambda arg: arg_is_file(arg, 'Config'),
        help='path to the tests configuration file. Default: "pluma.yml"')
    parser.add_argument(
        '-t', '--target', default='pluma-target.yml',
        type=lambda arg: arg_is_file(arg, 'Target config'),
        help='path to the target configuration file. Default: "pluma-target.yml"')
    parser.add_argument(
        '--plugin', action='append',
        type=lambda arg: arg_is_dir(arg, 'Plugins'),
        help='load plugin modules from directory path')
    parser.add_argument(
        '-f', '--force', action='store_const', const=True,
        help='force operation instead of prompting')
    parser.add_argument(
        '--silent', action='store_const', const=True,
        help='silence all output')
    parser.add_argument(
        '--debug', action='store_const', const=True,
        help='enable debug information')

    args = parser.parse_args()
    return args


def set_log_mode(args):
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


def main():
    args = parse_arguments()

    set_log_mode(args)
    tests_config_path = args.config
    target_config_path = args.target

    if args.plugin:
        for plugin_dir in args.plugin:
            load_plugin_modules(plugin_dir)

    try:
        command = args.command

        if command in [RUN_COMMAND, CHECK_COMMAND, TESTS_COMMAND]:
            pluma_context, tests_config = Pluma.create_context_from_files(tests_config_path,
                                                                          target_config_path)

            if command == RUN_COMMAND:
                success = Pluma.execute_run(pluma_context, tests_config)
                exit(0 if success else 1)
            elif command == CHECK_COMMAND:
                Pluma.execute_run(pluma_context, tests_config,
                                check_only=True)
            elif command == TESTS_COMMAND:
                Pluma.execute_tests(tests_config_path)

        elif command == CLEAN_COMMAND:
            Pluma.execute_clean(args.force)
        elif command == VERSION_COMMAND:
            log.log(Pluma.version(), level=LogLevel.IMPORTANT)
    except TestsConfigError as e:
        log.error(
            [f'Error while parsing the tests configuration ({tests_config_path}):', str(e)])
        exit(-2)
    except TargetConfigError as e:
        log.error(
            [f'Error while parsing the target configuration ({target_config_path}):', str(e)])
        exit(-3)
    except TestsBuildError as e:
        log.error(
            ['Error while building tests:', str(e)])
        exit(-4)
    except Exception as e:
        if log.mode in [LogMode.VERBOSE, LogMode.DEBUG]:
            traceback.print_exc()
        log.error(repr(e))
        exit(-1)


if __name__ == "__main__":
    main()
