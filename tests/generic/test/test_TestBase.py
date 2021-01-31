from pluma.test import NoopTest


def test_TestBase_should_include_class_name_in_generated_test_name():
    test1 = NoopTest()
    assert type(test1).__name__ in str(test1)

    test2 = NoopTest(test_name='test 1 name')
    assert type(test1).__name__ in str(test2)


def test_TestBase_should_include_name_in_generated_test_name():
    test1 = NoopTest(test_name='test 1 name')
    assert 'test 1 name' in str(test1)


def test_TestBase_should_generate_unique_names():

    test1 = NoopTest()
    test2 = NoopTest()
    test3 = NoopTest()
    test_names = {str(test1), str(test2), str(test3)}
    assert None not in test_names
    assert len(test_names) == 3


def test_TestBase_same_name_parameter_should_still_generate_unique_name():
    name = 'test name'
    test1 = NoopTest(test_name=name)
    test2 = NoopTest(test_name=name)
    assert str(test1) != str(test2)
