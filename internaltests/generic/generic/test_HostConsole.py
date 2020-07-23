from farmcore import HostConsole

def test_hostconsole_bin_sh_send():
    console = HostConsole('/bin/sh')

    __, matched = console.send(
        cmd='echo $SHELL',
        match='/bin/.*sh',
        timeout=0.5
    )

    assert matched