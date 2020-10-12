from pluma.test.testrunner import TestRunnerParallel
from unittest.mock import MagicMock, Mock, patch
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


def test_TestRunner_should_run_hook_tasks_from_all_tests(mock_board):
    class MyTest1(TestBase):
        def setup(self):
            pass

    class MyTest2(TestBase):
        def test_body(self):
            pass

    class MyTest3(TestBase):
        def teardown(self):
            pass

    test1 = MagicMock(MyTest1(mock_board))
    test2 = MagicMock(MyTest2(mock_board))
    test3 = MagicMock(MyTest3(mock_board))

    TestRunner(
        board=mock_board,
        tests=[test1, test2, test3]
    ).run()

    test1.setup.assert_called_once()
    test2.test_body.assert_called_once()
    test3.teardown.assert_called_once()


def test_TestRunnerParallel_should_run_hook_tasks_from_all_tests(mock_board):
    class MyTest1(TestBase):
        def setup(self):
            pass

    class MyTest2(TestBase):
        def test_body(self):
            pass

    class MyTest3(TestBase):
        def teardown(self):
            pass

    test1 = MagicMock(MyTest1(mock_board))
    test2 = MagicMock(MyTest2(mock_board))
    test3 = MagicMock(MyTest3(mock_board))

    TestRunnerParallel(
        board=mock_board,
        tests=[test1, test2, test3]
    ).run()

    test1.setup.assert_called_once()
    test2.test_body.assert_called_once()
    test3.teardown.assert_called_once()


def test_TestRunner_should_swallow_test_exceptions(mock_board):
    class MyTest(TestBase):
        def test_body(self):
            raise RuntimeError

    runner = TestRunner(
        board=mock_board,
        tests=MyTest(mock_board)
    )

    runner.run()


def test_TestRunner_should_run_teardown_if_test_body_raises_exception(mock_board):
    class MyTest(TestBase):
        def test_body(self):
            raise RuntimeError

        def teardown(self):
            pass

    test = MyTest(mock_board)
    test.teardown = Mock()

    runner = TestRunner(
        board=mock_board,
        tests=test
    )

    runner.run()

    test.teardown.assert_called_once()


def test_TestRunner_should_not_run_teardown_if_setup_raises_exception(mock_board):
    class MyTest(TestBase):
        def setup(self):
            raise RuntimeError

        def teardown(self):
            pass

    test = MyTest(mock_board)
    test.teardown = Mock()

    runner = TestRunner(
        board=mock_board,
        tests=test
    )

    # Not checking for exceptions in this test
    try:
        runner.run()
    except Exception:
        pass

    test.teardown.assert_not_called()


def test_TestRunner_should_not_run_more_tests_if_failure_and_no_continue_on_fail(mock_board):
    class MyTest1(TestBase):
        def test_body(self):
            raise RuntimeError

    class MyTest2(TestBase):
        def test_body(self):
            pass

    test1 = MyTest1(mock_board)
    test2 = MagicMock(MyTest2(mock_board))

    TestRunner(
        board=mock_board,
        tests=[test1, test2],
        continue_on_fail=False
    ).run()

    test2.test_body.assert_not_called()


def test_TestRunner_should_run_more_tests_if_failure_but_continue_on_fail(mock_board):
    class MyTest1(TestBase):
        def test_body(self):
            raise RuntimeError

    class MyTest2(TestBase):
        def test_body(self):
            pass

    test1 = MyTest1(mock_board)
    test2 = MagicMock(MyTest2(mock_board))

    TestRunner(
        board=mock_board,
        tests=[test1, test2],
        continue_on_fail=True
    ).run()

    test2.test_body.assert_called_once()


def test_TestRunner_should_attempt_email_if_tests_failure_and_email_on_fail(mock_board):
    class MyTest(TestBase):
        def test_body(self):
            raise RuntimeError

    test = MyTest(mock_board)

    runner = TestRunner(
        board=mock_board,
        tests=test,
        email_on_fail=True
    )

    with patch('pluma.utils.send_exception_email') as send_exception_email:
        runner.run()
        send_exception_email.assert_called_once()


def test_TestRunner_should_not_attempt_email_if_tests_failure_and_email_on_fail_false(mock_board):
    class MyTest(TestBase):
        def test_body(self):
            raise RuntimeError

    test = MyTest(mock_board)

    runner = TestRunner(
        board=mock_board,
        tests=test,
        email_on_fail=False
    )

    with patch('pluma.utils.send_exception_email') as send_exception_email:
        runner.run()
        send_exception_email.assert_not_called()


def test_TestRunner_should_have_expected_data_single_test(mock_board):
    # This test checks a bit much, but at least ensures data structure matches
    class MyTest(TestBase):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.settings['hello'] = 'world'

        def test_body(self):
            self.save_data({'foo': 'bar'})

        def teardown(self):
            pass

        def random_func_not_hook(self):
            pass

    expected_data = {
        'test_TestRunner.MyTest': {
            'data': {
                'foo': 'bar'
            },
            'order': 0,
            'settings': {
                'hello': 'world'
            },
            'tasks': {
                'failed': {},
                'ran': ['test_body', 'teardown']}
        }
    }

    runner = TestRunner(
        board=mock_board,
        tests=MyTest(mock_board)
    )

    runner.run()

    assert runner.data == expected_data
