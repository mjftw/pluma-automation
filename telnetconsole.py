#!/usb/bin/env python3

import sys
import time

from hostconsole import HostConsole


class TelnetConsole(HostConsole):
    def __init__(self, host, user, pw):
        self.host = host
        self.user = user
        self.pw = pw
        super.__init__('telent {}'.format(host))

    def login(self):
        pass
