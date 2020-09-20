import pytest

from pluma.cli import PlumaConfigPreprocessor


def test_PlumaConfigPreprocessor_should_keep_original_with_no_variables():
    preprocessor = PlumaConfigPreprocessor(None)
    original_content = 'content: value\notherline\nan a new one.'
    assert preprocessor.preprocess(original_content) == original_content


def test_PlumaConfigPreprocessor_should_replace_variables():
    preprocessor = PlumaConfigPreprocessor({'abc': 'abcvalue', 'def': 'defvalue'})
    result = preprocessor.preprocess('content: ${abc},\n${def}: ${abc}')
    assert result == 'content: abcvalue,\ndefvalue: abcvalue'


def test_PlumaConfigPreprocessor_should_error_on_missing_variable():
    preprocessor = PlumaConfigPreprocessor({'abc': 'abcvalue'})

    with pytest.raises(Exception):
        preprocessor.preprocess('content: ${abc},\n${def}: ${abc}')
