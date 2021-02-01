import pytest
from unittest.mock import Mock

from pluma.test import TestBase, TestGroup, GroupedTest, Session, Plan

GROUPED_TEST_CLASSES = [GroupedTest, Session, Plan]


@pytest.mark.parametrize('group_test_class', GROUPED_TEST_CLASSES)
def test_GroupedTest_default_constructor(group_test_class):
    grouped_test = group_test_class()
    assert grouped_test.test_group.tests == []


@pytest.mark.parametrize('group_test_class', GROUPED_TEST_CLASSES)
def test_GroupedTest_set_tests_from_constructor(group_test_class, mock_board):
    class MyTest1(TestBase):
        def test_body(self):
            pass

    class MyTest2(TestBase):
        def test_body(self):
            pass

    test1, test2 = MyTest1(mock_board), MyTest2(mock_board)
    grouped_test = group_test_class(tests=[test1, test2])

    assert isinstance(grouped_test.test_group.tests[0], test1.__class__)
    assert isinstance(grouped_test.test_group.tests[1], test2.__class__)


@pytest.mark.parametrize('group_test_class', GROUPED_TEST_CLASSES)
def test_GroupedTest_set_tests_manually(group_test_class, mock_board):
    class MyTest1(TestBase):
        def test_body(self):
            pass

    class MyTest2(TestBase):
        def test_body(self):
            pass

    test1, test2 = MyTest1(mock_board), MyTest2(mock_board)
    grouped_test = group_test_class()
    grouped_test.test_group = TestGroup(tests=[test1, test2])
    assert isinstance(grouped_test.test_group.tests[0], test1.__class__)
    assert isinstance(grouped_test.test_group.tests[1], test2.__class__)


def test_GroupedTest_should_not_call_test_methods(mock_board):
    class MyTest1(TestBase):
        def test_body(self):
            pass

    class MyTest2(TestBase):
        def test_body(self):
            pass

    test1 = MyTest1(mock_board)
    test1.setup = Mock()
    test1.test_body = Mock()
    test1.teardown = Mock()

    grouped_test = GroupedTest(tests=[test1])
    grouped_test.setup()
    grouped_test.test_body()
    grouped_test.teardown()

    test1.setup.assert_not_called()
    test1.test_body.assert_not_called()
    test1.teardown.assert_not_called()
