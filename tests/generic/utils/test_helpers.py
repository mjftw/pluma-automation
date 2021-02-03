import pytest
from pluma.utils import resize_string


def test_resize_string_should_pad():
    assert resize_string('123', length=6) == '123   '


def test_resize_string_should_elide():
    assert resize_string('123456789', length=6) == '123...'


def test_resize_string_should_error_on_length_too_small():
    with pytest.raises(ValueError):
        resize_string('123', length=3)
