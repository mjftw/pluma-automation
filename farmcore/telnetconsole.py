#!/usb/bin/env python3

import sys
import time

from .hostconsole import HostConsole


class TelnetConsole(HostConsole):
    def __init__(self, host):
        self.host = host
        super().__init__('telnet {}'.format(host))