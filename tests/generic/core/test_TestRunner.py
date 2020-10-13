from unittest.mock import MagicMock, Mock
from pluma.test import TestRunner, TestBase


def test_TestRunner_should_run_setup_task_if_present(mock_board):
    class MyTest(TestBase):
        def setup(self):
            pass

    test = MagicMock(MyTest(mock_board))

    TestRunner(
        board=mock_board,
        tests=test
    ).run()

    test.setup.assert_called_once()


def test_TestRunner_should_run_test_body_task_if_present(mock_board):
    class MyTest(TestBase):
        def test_body(self):
            pass

    test = MagicMock(MyTest(mock_board))

    TestRunner(
        board=mock_board,
        tests=test
    ).run()

    test.test_body.assert_called_once()


def test_TestRunner_should_run_teardown_task_if_present(mock_board):
    class MyTest(TestBase):
        def teardown(self):
            pass

    test = MagicMock(MyTest(mock_board))

    TestRunner(
        board=mock_board,
        tests=test
    ).run()

    test.teardown.assert_called_once()


def test_TestRunner_should_not_non_hook_functions(mock_board):
    class MyTest(TestBase):
        def foobar(self):
            pass

    test = MagicMock(MyTest(mock_board))

    TestRunner(
        board=mock_board,
        tests=test
    ).run()

    test.foobar.assert_not_called()
