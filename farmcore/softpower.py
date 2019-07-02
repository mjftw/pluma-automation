from .baseclasses import PowerBase, ConsoleBase
from .exceptions import PDUError


class SoftPower(PowerBase):
    def __init__(self, console, on_cmd=None, off_cmd=None):
        assert isinstance(console, ConsoleBase)

        self.console = console
        self.on_cmd = on_cmd
        self.off_cmd = off_cmd

        PowerBase.__init__(self)

    @PowerBase.on
    def on(self):
        if self.on_cmd:
            self.console.send(self.on_cmd)
        else:
            self.error('No on_cmd, cannot soft power on', PDUError)

    @PowerBase.off
    def off(self):
        if self.off_cmd:
            self.console.send(self.off_cmd)
        else:
            self.error('No off_cmd, cannot soft power off', PDUError)
