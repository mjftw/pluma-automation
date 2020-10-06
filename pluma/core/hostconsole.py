from .baseclasses import ConsoleBase
from .dataclasses import SystemContext


class HostConsole(ConsoleBase):
    def __init__(self, command, system: SystemContext = None):
        self.command = command
        super().__init__(system=system)

        self._requires_login = False

    def __repr__(self):
        command = self.command
        if len(command) > 30:
            command = f'{self.command[:27]}...'

        return f'{self.__class__.__name__}[{command}]'

    def open(self):
        self.engine.open(console_cmd=self.command)

    def interact(self):
        if not self.is_open:
            self.open()
        self.engine.interact()
