from pluma.test import TestBase


class DummyTest(TestBase):
    def test_body(self):
        pass


def test_TestBase_should_include_class_name_in_generated_test_name():
    test1 = DummyTest()
    assert type(test1).__name__ in str(test1)

    test2 = DummyTest(test_name='test 1 name')
    assert type(test1).__name__ in str(test2)


def test_TestBase_should_include_name_in_generated_test_name():
    test1 = DummyTest(test_name='test 1 name')
    assert 'test 1 name' in str(test1)


def test_TestBase_should_generate_unique_names():

    test1 = DummyTest()
    test2 = DummyTest()
    test3 = DummyTest()
    test_names = {str(test1), str(test2), str(test3)}
    assert None not in test_names
    assert len(test_names) == 3


def test_TestBase_same_name_parameter_should_still_generate_unique_name():
    name = 'test name'
    test1 = DummyTest(test_name=name)
    test2 = DummyTest(test_name=name)
    assert str(test1) != str(test2)
