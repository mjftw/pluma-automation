def test_SSHConsole_does_require_login(minimal_ssh_console):
    assert minimal_ssh_console.requires_login is False
