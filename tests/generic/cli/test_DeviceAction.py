import time
import pytest
from unittest.mock import MagicMock

from pluma import Board
from pluma.core.baseclasses import ConsoleBase
from pluma.test import TaskFailed
from pluma.cli import DeviceActionRegistry, DeviceActionBase, LoginAction, WaitAction, \
    WaitForPatternAction, SetAction, DeployAction
from utils import nonblocking


def test_DeviceActionRegistry_register_should_register_class():
    action_name = 'someaction'

    @DeviceActionRegistry.register(action_name)
    class SomeAction(DeviceActionBase):
        def execute(self):
            pass

    assert DeviceActionRegistry.action_class(action_name) == SomeAction
    assert action_name in DeviceActionRegistry.all_actions()


def test_DeviceActionRegistry_create_should_register_class(mock_board):
    action_name = 'someotheraction'

    @DeviceActionRegistry.register(action_name)
    class SomeAction(DeviceActionBase):
        def execute(self):
            pass

    action = DeviceActionRegistry.create(mock_board, action_name)
    assert isinstance(action, SomeAction)


def test_LoginAction_should_call_login(mock_board):
    action = LoginAction(mock_board)
    action.execute()
    mock_board.login.assert_called_once()


def test_WaitAction_should_wait(mock_board):
    wait = 0.5
    action = WaitAction(mock_board, duration=wait)
    start = time.time()
    action.execute()
    end = time.time()

    elapsed = end-start
    assert 0.8*wait < elapsed < 1.2*wait


def test_WaitForPatternAction_should_fail_on_timeout(mock_board):
    mock_board.console.wait_for_match.return_value = None
    action = WaitForPatternAction(mock_board, pattern='abc')

    with pytest.raises(TaskFailed):
        action.execute()


def test_WaitForPatternAction_should_succeed_when_matched(mock_board):
    mock_board.console.wait_for_match.return_value = 'abcde'
    action = WaitForPatternAction(mock_board, pattern='abc')

    action.execute()


def test_WaitForPatternAction_should_succeed_when_matched_proxy_console(serial_console_proxy):
    mock_board = Board("board", console=serial_console_proxy.console)
    expected_pattern = 'abc'
    action = WaitForPatternAction(
        mock_board, pattern=expected_pattern)

    async_action = nonblocking(action.execute)

    # Wait to make sure what we write isn't discarded
    time.sleep(0.1)
    serial_console_proxy.proxy.write('some content')
    serial_console_proxy.proxy.write('abc\n')

    async_action.get()


def test_WaitForPatternAction_should_fail_when_no_matched_proxy_console(serial_console_proxy):
    mock_board = Board("board", console=serial_console_proxy.console)
    expected_pattern = 'abc'
    action = WaitForPatternAction(
        mock_board, pattern=expected_pattern, timeout=1)

    async_action = nonblocking(action.execute)

    # Wait to make sure what we write isn't discarded
    time.sleep(0.1)
    serial_console_proxy.proxy.write('some content')
    serial_console_proxy.proxy.write('and more\n')

    with pytest.raises(TaskFailed):
        async_action.get()


def test_SetAction_should_set_console():
    ssh_console = MagicMock(ConsoleBase)
    serial_console = MagicMock(ConsoleBase)
    board = Board("board", console={
                  'ssh': ssh_console, 'serial': serial_console})

    action = SetAction(board, device_console='ssh')
    action.execute()

    assert board.console is ssh_console

    action = SetAction(board, device_console='serial')
    action.execute()
    assert board.console is serial_console


@pytest.mark.parametrize('console_type', ['ssh', 'serial'])
def test_SetAction_should_error_if_no_console(mock_board, console_type):
    mock_board.get_console.return_value = None
    with pytest.raises(ValueError):
        SetAction(mock_board, device_console=console_type)


def test_DeployAction_constructor_should_work(mock_board):
    DeployAction(board=mock_board, files=['myfile'], destination='there')


def test_DeployAction_should_error_if_files_is_not_a_list(mock_board):
    with pytest.raises(ValueError):
        DeployAction(board=mock_board, files='myfile', destination='there')


def test_DeployAction_should_error_if_console_does_not_support_copy(mock_board):
    mock_board.console.support_file_copy = False
    mock_board.console.copy_to_target = MagicMock()

    action = DeployAction(board=mock_board, files=['myfile'], destination='there')
    with pytest.raises(TaskFailed):
        action.execute()


def test_DeployAction_should_deploy_files(mock_board):
    mock_board.console.support_file_copy = True
    mock_board.console.copy_to_target = MagicMock()
    files = ['/a/abc.so', 'other']
    destination = '/some/where'
    timeout = 666

    action = DeployAction(board=mock_board, files=files, destination=destination,
                          timeout=timeout)
    action.execute()

    assert mock_board.console.copy_to_target.call_count == len(files)
    index = 0
    for call in mock_board.console.copy_to_target.call_args_list:
        assert call[1]['source'] == files[index]
        assert call[1]['destination'] == destination
        assert call[1]['timeout'] == timeout
        index += 1
