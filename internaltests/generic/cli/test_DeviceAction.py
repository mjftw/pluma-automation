import time
import pytest

from farmcore import Board
from farmtest import TaskFailed
from farmcli import DeviceActionRegistry, DeviceActionBase, LoginAction, WaitAction, WaitForPatternAction

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
    action = WaitAction(mock_board, duration=1.5)
    start = time.time()
    action.execute()
    end = time.time()

    elapsed = end-start
    assert elapsed > 1 and elapsed < 2


def test_WaitForPatternAction_should_fail_on_timeout(mock_board):
    mock_board.console.wait_for_match.return_value = None
    action = WaitForPatternAction(mock_board, pattern='abc')

    with pytest.raises(TaskFailed):
        action.execute()


def test_WaitForPatternAction_should_succeed_when_matched(mock_board):
    mock_board.console.wait_for_match.return_value = 'abcde'
    action = WaitForPatternAction(mock_board, pattern='abc')

    action.execute()


def test_WaitForPatternAction_should_succeed_when_matched_proxy_console(mock_board, serial_console_proxy):
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


def test_WaitForPatternAction_should_fail_when_no_matched_proxy_console(mock_board, serial_console_proxy):
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
