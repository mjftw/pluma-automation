from traceback import format_exc
from types import ModuleType
from typing import Dict, Iterable, List, Tuple, Union
import pty
import os
import sys
import time
from pytest import fixture
from unittest.mock import MagicMock, patch
import traceback
import tempfile
import textwrap
import shutil
import yaml
import pluma.plugins

from utils import OsFile
from pluma import Board, SerialConsole, SoftPower, SSHConsole
from pluma.core.baseclasses import ConsoleBase
from pluma.core.dataclasses import SystemContext, Credentials
from pluma.core.mocks import ConsoleMock
from pluma import __main__


@fixture
def soft_power():
    mock_console = MagicMock(ConsoleMock())

    return SoftPower(
        console=mock_console,
        on_cmd='MOCK ON',
        off_cmd='MOCK OFF'
    )


class SerialConsoleProxy:
    def __init__(self, proxy, console: ConsoleBase):
        self.proxy = proxy
        self.console = console

    def fake_reception(self, message: str, wait_time: int = 0.1):
        time.sleep(wait_time)
        self.proxy.write(message)

    def read_serial_output(self):
        # Give time for the data written to propagate
        return self.proxy.read(timeout=0.2)


@fixture
def serial_console_proxy():
    # === Setup ===
    master, slave = pty.openpty()

    slave_device = os.ttyname(slave)

    console = SerialConsole(
        port=slave_device,
        baud=115200,  # Baud Doesn't really matter as virtual tty,
        encoding='utf-8'
    )

    proxy = OsFile(master, console.encoding)

    # Clear master file just in case
    proxy.read(timeout=0)

    # === Return Fixture ===
    yield SerialConsoleProxy(proxy, console)

    # === Teardown ===
    console.close()

    for fd in [master, slave]:
        try:
            os.close(fd)
        except OSError:
            pass


@fixture
def minimal_ssh_console():
    return SSHConsole(target="localhost", system=SystemContext(Credentials("root")))


@fixture
def mock_console():
    return MagicMock(ConsoleBase)


@fixture
def mock_board(mock_console):
    mock_board = MagicMock(Board)
    mock_board.console = mock_console

    return mock_board


@fixture
def target_config():
    return {}


@fixture
def ssh_config():
    return {
        'target': '123',
        'login': 'abc'
    }


@fixture
def serial_config():
    return {
        'port': 'abc',
        'baud': 123,
    }


@fixture
def pluma_cli(capsys):
    '''Get a function that can be used to call the Pluma CLI with given args and catches exits'''
    def pluma_cli(args: Iterable[str] = []):
        assert isinstance(args, Iterable)

        # Override actual CLI arguments with supplied
        with patch.object(sys, 'argv', [sys.argv[0], *args]):
            try:
                __main__.main()
            except SystemExit as e:
                if e.code != 0:
                    readouterr = capsys.readouterr()
                    e_msg = f'Pluma CLI exited with code {e.code}'
                    print(
                        f'{e_msg}',
                        f'{os.linesep}stdout: {readouterr.out}' if readouterr.out else '',
                        f'{os.linesep}stderr: {readouterr.err}' if readouterr.err else '',
                    )
                    traceback.print_exc()

                    raise RuntimeError(e_msg)

    return pluma_cli


@fixture
def temp_file():
    '''Return a function that creates temporary files with content and returns their names.'''
    tempdir = tempfile.mkdtemp()

    def temp_file(content: str = None, dedent: bool = True) -> str:
        '''Create a temporary file with the given content and return its name.
        Set dedent to allow natural indentation in multiline strings.
        '''
        _, filename = tempfile.mkstemp(dir=tempdir)

        if content:
            if dedent:
                # Remove leading newlines and global indent
                content = textwrap.dedent(content)
                content = content.lstrip(os.linesep)

            with open(filename, 'w') as f:
                f.write(content)

        return filename

    # Return the function used to create temporary files
    yield temp_file

    # Cleanup
    shutil.rmtree(tempdir)


def child_path(obj: Union[type, ModuleType, str], parent: Union[type, ModuleType]) -> str:
    def get_name(to_check):
        if isinstance(to_check, type):
            return f'{to_check.__module__}.{to_check.__name__}'
        elif isinstance(to_check, ModuleType):
            return f'{to_check.__name__}'
        elif isinstance(to_check, str):
            return to_check
        else:
            raise AttributeError(f'{to_check} must be a class, module or module path str')

    obj_name = get_name(obj)
    parent_name = get_name(parent)

    if not obj_name.startswith(parent_name):
        raise AttributeError(f'{obj_name} is not a child of {parent_name}')

    # Add 1 to jump over the dot between parent name and child
    return obj_name[len(parent_name) + 1:]


@fixture
def pluma_config_file(temp_file):
    '''Return a function to create a temporary pluma test config file'''
    plugins_root = pluma.plugins

    def pluma_config_file(core_tests_params: List[Tuple[type, Dict[str, str]]] = None,
                          settings: dict = None) -> str:
        '''Create a temporary pluma config file and return its path.
        `core_tests_params` should be a list of tuples of test class and test params.
        E.g. (test_class, {param1: value1, param_2: value2})
        '''
        if core_tests_params and not isinstance(core_tests_params, Iterable):
            core_tests_params = [core_tests_params]

        tab = ' '*4
        config_lines = []

        if settings:
            settings = {'settings': {**settings}}
            settings_lines = yaml.dump(settings).split(os.linesep)
            config_lines.extend(settings_lines)

        config_lines.append('sequence:')
        if core_tests_params:
            includes = [f'{child_path(cls.__module__, plugins_root)}.{cls.__name__}'
                        for cls, _ in core_tests_params]
            # Get unique includes, preserving order
            includes = list(dict.fromkeys(includes))
            includes = f'[{", ".join((includes))}]'

            config_lines.append('- core_tests:')
            config_lines.append(f'{tab}include: {includes}')
            config_lines.append(f'{tab}parameters:')

            for cls, params in core_tests_params:
                assert isinstance(cls, type)
                assert isinstance(params, dict)

                config_lines.append(f'{tab*2}{child_path(cls, plugins_root)}:')
                for key, val in params.items():
                    if isinstance(val, list):
                        val = f'[{", ".join(val)}]'

                    config_lines.append(f'{tab*3}{key}: {val}')

        file_content = os.linesep.join(config_lines)

        return temp_file(file_content)

    return pluma_config_file
