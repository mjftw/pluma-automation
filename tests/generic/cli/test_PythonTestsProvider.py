import pytest

from pluma.cli import PythonTestsProvider


@pytest.mark.parametrize('match, test',
                         [('abc', 'abc'), ('abc', 'abc.def'),
                          ('abc.def', 'abc.def'), ('abc.def', 'abc.def.ghi')])
def test_PythonTestsProvider_test_match_should_match(match, test):
    assert PythonTestsProvider.test_match(test, match_string=match) is True


@pytest.mark.parametrize('match, test',
                         [('abc', 'abcd'), ('abc', 'def.abc')])
def test_PythonTestsProvider_test_match_should_not_match(match, test):
    assert PythonTestsProvider.test_match(test, match_string=match) is False
