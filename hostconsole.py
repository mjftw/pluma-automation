#!/usb/bin/env python3

import sys
import time
import pexpect
import pexpect.fdpexpect

from console import Console

class HostConsole(Console):
    def __init__(self, command):
        self.command = command
        self._pex = None
        super().__init__()

    @property
    def is_open(self):
        if self._pex and self._pex.isalive:
            return True
        else:
            return False

    def open(self):
        self._pex = pexpect.spawn(self.command, timeout=0.01)
        if not self.is_open:
            raise RuntimeError("Could not start host console");

    def close(self):
        self._pex.sendintr()
        self._pex = None

    def interact(self):
        if not self.is_open:
            self.open()
        self._pex.interact()
