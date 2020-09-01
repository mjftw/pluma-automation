from .baseclasses import PowerBase, ConsoleBase
from .exceptions import PDUError


class SoftPower(PowerBase):
    def __init__(self, console, on_cmd=None, off_cmd=None,
                 reboot_cmd=None, reboot_delay=None):
        assert isinstance(console, ConsoleBase)

        self.console = console
        self.on_cmd = on_cmd
        self.off_cmd = off_cmd
        self.reboot_cmd = reboot_cmd

        if not self.reboot_cmd and not self.on_cmd and not self.off_cmd:
            self.reboot_cmd = 'reboot || shutdown -r now || systemctl reboot'

        PowerBase.__init__(self, reboot_delay)

    @PowerBase.on
    def on(self):
        if self.on_cmd is not None:
            self.console.send(self.on_cmd)
        else:
            self.error('No "on_cmd", cannot soft power on', PDUError)

    @PowerBase.off
    def off(self):
        if self.off_cmd is not None:
            self.console.send(self.off_cmd)
        else:
            self.error('No "off_cmd", cannot soft power off', PDUError)

    def reboot(self):
        if self.reboot_cmd is not None:
            self.log(f'{str(self)}: Rebooting...')
            self.console.send(self.reboot_cmd)
        elif self.off_cmd and self.on_cmd:
            PowerBase.reboot(self)
        else:
            self.error('Need either "reboot_cmd" or "both off_cmd" and "on_cmd" '
                       'to soft reboot', PDUError)
