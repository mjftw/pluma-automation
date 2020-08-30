
def test_SSHConsole_does_require_login(serial_console_proxy):
    assert serial_console_proxy.console.requires_login is True
