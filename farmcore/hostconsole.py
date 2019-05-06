import pexpect
import pexpect.fdpexpect

from .baseclasses import ConsoleBase, CannotOpen


class HostConsole(ConsoleBase):
    def __init__(self, command):
        self.command = command
        self._pex = None
        super().__init__()

    @property
    def is_open(self):
        if self._pex and self._pex.isalive():
            return True
        else:
            return False

    def open(self):
        self._pex = pexpect.spawn(self.command, timeout=0.01)
        if not self.is_open:
            raise CannotOpen

    def close(self):
        self._pex.sendintr()
        self._pex = None

    def interact(self):
        if not self.is_open:
            self.open()
        self._pex.interact()

