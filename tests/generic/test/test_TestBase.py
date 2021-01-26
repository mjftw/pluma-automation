from pluma.test import TestBase


def test_TestBase_should_generate_unique_names():
    test1 = TestBase()
    test2 = TestBase()
    assert str(test1)
    assert str(test2)
    assert str(test1) != str(test2)
    test3 = TestBase()
    assert str(test2) != str(test3)


def test_TestBase_should_include_name_in_generated_test_name():
    test1 = TestBase(test_name='test 1 name')
    assert 'test 1 name' in str(test1)


def test_TestBase_same_name_parameter_should_still_generate_unique_name():
    name = 'test name'
    test1 = TestBase(test_name=name)
    test2 = TestBase(test_name=name)
    assert str(test1) != str(test2)
