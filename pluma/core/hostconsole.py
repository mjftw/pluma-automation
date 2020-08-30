import pexpect
import pexpect.fdpexpect

from .baseclasses import ConsoleBase, SystemContext
from .exceptions import ConsoleCannotOpenError


class HostConsole(ConsoleBase):
    def __init__(self, command, system: SystemContext = None):
        self.command = command
        self._pex = None
        super().__init__(system=system)

    def __repr__(self):
        command = self.command
        if len(command) > 30:
            command = f'{self.command[:27]}...'

        return f'{self.__class__.__name__}[{command}]'

    @property
    def is_open(self):
        if self._pex and self._pex.isalive():
            return True
        else:
            return False

    @ConsoleBase.open
    def open(self):
        try:
            self._pex = pexpect.spawn(self.command, timeout=0.01)
            self._pex.timeout = 0.5
            assert self.is_open
        except Exception:
            raise ConsoleCannotOpenError

    @ConsoleBase.close
    def close(self):
        self._pex.sendintr()
        self._pex = None

    def interact(self):
        if not self.is_open:
            self.open()
        self._pex.interact()
