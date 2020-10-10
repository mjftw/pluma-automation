import time
import pytest
import tempfile
from pluma.core.baseclasses import PexpectEngine

from utils import nonblocking


def test_PexpectEngine_open_shell_should_succeed():
    engine = PexpectEngine()
    engine.open(console_cmd='sh')
    assert engine.is_open


def test_PexpectEngine_close_shell_should_succeed():
    engine = PexpectEngine()
    engine.open(console_cmd='sh')
    engine.close()
    assert engine.is_open is False


def test_PexpectEngine_open_fd_should_succeed():
    with tempfile.TemporaryFile() as tmp:
        engine = PexpectEngine()
        engine.open(console_fd=tmp.fileno())
        assert engine.is_open


def test_PexpectEngine_close_fd_should_succeed():
    with tempfile.TemporaryFile() as tmp:
        engine = PexpectEngine()
        engine.open(console_fd=tmp.fileno())
        engine.close()
        assert engine.is_open is False


def test_PexpectEngine_wait_for_match_return_received_and_match_if_matched():
    pass


def test_PexpectEngine_wait_for_match_return_received_if_not_matched():
    pass
