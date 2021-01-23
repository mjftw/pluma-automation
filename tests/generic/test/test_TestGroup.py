from pluma.test import TestGroup
from pluma.test import TestBase


def test_TestGroup_default_constructor():
    group = TestGroup()
    assert group.tests == []
    assert group.name is None


def test_TestGroup_add_test_from_constructor(mock_board):
    class MyTest1(TestBase):
        def test_body(self):
            pass

    class MyTest2(TestBase):
        def test_body(self):
            pass

    test1, test2 = MyTest1(mock_board), MyTest2(mock_board)
    group = TestGroup(tests=[test1, test2])

    assert isinstance(group.tests[0], test1.__class__)
    assert isinstance(group.tests[1], test2.__class__)


def test_TestGroup_add_test_method(mock_board):
    class MyTest1(TestBase):
        def test_body(self):
            pass

    class MyTest2(TestBase):
        def test_body(self):
            pass

    group = TestGroup()
    test1, test2 = MyTest1(mock_board), MyTest2(mock_board)
    group.add_test(test1)
    group.add_test(test2)

    assert isinstance(group.tests[0], test1.__class__)
    assert isinstance(group.tests[1], test2.__class__)


def test_TestGroup_set_tests(mock_board):
    class MyTest1(TestBase):
        def test_body(self):
            pass

    class MyTest2(TestBase):
        def test_body(self):
            pass

    group = TestGroup()
    test1, test2 = MyTest1(mock_board), MyTest2(mock_board)
    group.tests = [test1, test2]

    assert isinstance(group.tests[0], test1.__class__)
    assert isinstance(group.tests[1], test2.__class__)


def test_TestGroup_len_returns_test_count(mock_board):
    group = TestGroup()
    assert len(group) == 0

    class MyTest1(TestBase):
        def test_body(self):
            pass

    class MyTest2(TestBase):
        def test_body(self):
            pass

    group.add_test(MyTest1(mock_board))
    group.add_test(MyTest2(mock_board))

    assert len(group) == 2


def test_TestGroup_get_test_by_name_returns_none(mock_board):
    group = TestGroup()

    class MyTest1(TestBase):
        def test_body(self):
            pass

    class MyTest2(TestBase):
        def test_body(self):
            pass

    group.add_test(MyTest1(mock_board))
    group.add_test(MyTest2(mock_board))

    assert group.get_test_by_name('abcdef') is None


def test_TestGroup_get_test_by_name_returns_match(mock_board):
    group = TestGroup()

    class MyTest1(TestBase):
        def test_body(self):
            pass

    class MyTest2(TestBase):
        def test_body(self):
            pass

    group.add_test(MyTest1(mock_board))
    group.add_test(MyTest2(mock_board))

    test1 = group.tests[0]
    assert group.get_test_by_name(str(test1)) == test1
