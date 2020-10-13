import pytest
import tempfile
from pluma.test import ExecutableTest


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
