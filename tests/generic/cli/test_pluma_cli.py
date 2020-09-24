import pytest


def test_cli_should_error_on_missing_test_config(pluma_cli):
    with pytest.raises(RuntimeError):
        pluma_cli(['--config', '/this-file-doesnt-exist!'])

def test_cli_should_error_on_missing_target_config(pluma_cli):
    with pytest.raises(RuntimeError):
        pluma_cli(['--target', '/this-file-doesnt-exist!'])
