import pytest
import tempfile
from pathlib import Path

from pytest import fixture
from unittest.mock import MagicMock, patch

from pluma.test import ExecutableTest


@fixture
def executable_test(mock_board) -> ExecutableTest:
    return ExecutableTest(mock_board, executable_file='somename', host_file=False)


def test_executable_test_fixture_should_work(executable_test):
    pass


def test_ExecutableTest_should_pass_with_local_file(mock_board):
    with tempfile.NamedTemporaryFile() as f:
        ExecutableTest(mock_board, executable_file=f.name, host_file=True)


def test_ExecutableTest_should_error_with_missing_local_file(mock_board):
    with pytest.raises(ValueError):
        ExecutableTest(mock_board, executable_file='some/random/file', host_file=True)


def test_ExecutableTest_should_pass_with_any_target_file(mock_board):
    ExecutableTest(mock_board, executable_file='somename', host_file=False)


def test_ExecutableTest_should_error_if_running_target_file_on_host(mock_board):
    with pytest.raises(ValueError):
        ExecutableTest(mock_board, executable_file='somename', host_file=False, run_on_host=True)


def test_ExecutableTest_check_console_supports_copy_error_if_no_console(
        executable_test):
    with pytest.raises(ValueError):
        executable_test.check_console_supports_copy(console=None)


def test_ExecutableTest_check_console_supports_copy_error_if_console_not_compatible(
        executable_test, mock_console):

    mock_console.support_file_copy = False
    with pytest.raises(ValueError):
        executable_test.check_console_supports_copy(console=mock_console)


def test_ExecutableTest_check_console_supports_copy_error_ok_if_console_compatible(
        executable_test, mock_console):

    mock_console.support_file_copy = True
    executable_test.check_console_supports_copy(console=mock_console)


def test_ExecutableTest_deploy_executable_returns_path_and_folder(executable_test,
                                                                  mock_console):
    test_file = '/folder/abc'
    with patch('pluma.test.CommandRunner.run'):
        dest, tmp_folder = executable_test.deploy_file_in_tmp_folder(file=test_file,
                                                                     console=mock_console)
        assert tmp_folder
        assert dest
        assert executable_test.executable_file

        assert dest.startswith(tmp_folder)
        assert dest.endswith(Path(test_file).name)


def test_ExecutableTest_deploy_executable_calls_mkdir(executable_test,
                                                      mock_console):
    with patch('pluma.test.CommandRunner.run') as run:
        _, tmp_folder = executable_test.deploy_file_in_tmp_folder(file='/folder/abc',
                                                                  console=mock_console)

        assert tmp_folder
        run.assert_called_once()
        run_kwargs = run.call_args[1]
        assert run_kwargs['command'] == f'mkdir {tmp_folder}'
        assert run_kwargs['console'] == mock_console


def test_ExecutableTest_deploy_executable_calls_copy_to_target(executable_test,
                                                               mock_console):
    test_file = '/folder/abc'
    with patch('pluma.test.CommandRunner.run'):
        dest, _ = executable_test.deploy_file_in_tmp_folder(
            file=test_file, console=mock_console)
        mock_console.copy_to_target.assert_called_once_with(source=test_file,
                                                            destination=dest)


def test_ExecutableTest_test_body_on_host_execute_file(executable_test,
                                                       mock_console):
    executable_test.run_on_host = True
    executable_test.host_file = True

    with patch('pluma.test.CommandRunner.run') as run:
        executable_test.test_body()

        run.assert_called_once()
        run_kwargs = run.call_args[1]
        assert run_kwargs['command'] == executable_test.executable_file


def test_ExecutableTest_test_body_deploy_on_target(executable_test,
                                                   mock_console):
    executable_test.run_on_host = False
    executable_test.host_file = True
    target_tmp_dir = '/home/abc'
    target_executable = Path(target_tmp_dir)/'myapp'

    with patch('pluma.test.CommandRunner.run') as run:
        executable_test.deploy_file_in_tmp_folder = MagicMock()
        executable_test.deploy_file_in_tmp_folder.return_value = (
            target_executable, target_tmp_dir)

        executable_test.test_body()

        executable_test.deploy_file_in_tmp_folder.assert_called_once()
        run.assert_called()

        # First call to 'run' is to execute it
        run_kwargs = run.call_args_list[0][1]
        assert run_kwargs['command'] == target_executable

        # Second call to remove the tmp dir
        run_kwargs = run.call_args_list[1][1]
        assert run_kwargs['command'] == f'rm -r {target_tmp_dir}'


def test_ExecutableTest_test_body_on_target_execute_file(executable_test,
                                                         mock_console):
    executable_test.run_on_host = False
    executable_test.host_file = False

    with patch('pluma.test.CommandRunner.run') as run:
        executable_test.test_body()

        run.assert_called_once()
        assert run.call_args[1]['command'] == executable_test.executable_file
