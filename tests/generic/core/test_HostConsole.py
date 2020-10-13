import os
import pytest

from pluma import HostConsole


@pytest.mark.xfail(os.getenv('PLUMA_ENV') == 'CI', reason='CI fails to properly spawn a shell')
def test_hostconsole_bin_sh_send():
    console = HostConsole('/bin/sh')

    __, matched = console.send_and_expect(cmd='echo $SHELL',
                                          match='/bin/.*sh',
                                          timeout=0.5
                                          )

    assert matched
