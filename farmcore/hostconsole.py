import pexpect
import pexpect.fdpexpect

from .baseclasses import ConsoleBase
from .exceptions import ConsoleCannotOpenError


class HostConsole(ConsoleBase):
    def __init__(self, command):
        self.command = command
        self._pex = None
        super().__init__()

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
            # Wait to have a prompt, otherwise a connection failure can be is silently ignored
            self._pex.expect([r'\$', '>'], timeout=6)
        except:
            raise ConsoleCannotOpenError

        if not self.is_open:
            raise ConsoleCannotOpenError

    @ConsoleBase.close
    def close(self):
        self._pex.sendintr()
        self._pex = None

    def interact(self):
        if not self.is_open:
            self.open()
        self._pex.interact()
