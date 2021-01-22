import os
import subprocess
from typing import List, Optional

from pluma.core.baseclasses import PowerBase
from pluma.core import PDUError


class Uhubctl(PowerBase):
    ''' USB hub power control using uhubctl utility '''

    def __init__(self, location: str, port: int, reboot_delay: Optional[int] = None):
        PowerBase.__init__(self, reboot_delay)
        self.location = location
        self.port = port

        if not location or not port:
            raise PDUError('Uhubctl: "location" and/or "port" '
                           'attributes are missing')

    def uhubctl_command(self, action: str) -> List[str]:
        ''' Return a uhubctl command for the action provided '''
        # Unfortunately does require sudo, or custom udev rules
        return ['uhubctl',
                '--action', action,
                '--location', self.location,
                '--port', str(self.port)]

    def _handle_power_on(self):
        try:
            subprocess.check_output(self.uhubctl_command(action='on'),
                                    stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise Exception(
                f'Uhubctl: failed power ON location {self.location} and port {self.port}.'
                'Is "uhubctl" installed?'
                'Consider adding a udev rule in "/etc/udev/rules.d/50-uhubctl.rules"'
                '(SUBSYSTEM=="usb", ATTR{idVendor}=="<your_device_vendor>", MODE="0666"),'
                'or running pluma as root/sudo, if required.'
                f'{os.linesep}{os.linesep}{e.output.decode()}')

    def _handle_power_off(self):
        try:
            subprocess.check_output(self.uhubctl_command(action='off'),
                                    stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise Exception(
                f'Uhubctl: failed power ON location {self.location} and port {self.port}:'
                f'{os.linesep}{e.output.decode()}')
