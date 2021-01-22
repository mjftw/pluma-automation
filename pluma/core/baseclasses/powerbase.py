import time
from abc import ABC, abstractmethod

from .hardwarebase import HardwareBase


class PowerBase(HardwareBase, ABC):
    def __init__(self, reboot_delay: float = None):
        self.reboot_delay = reboot_delay or 0.5

    def on(self):
        '''Turn on the power control'''
        self.log(f'{str(self)}: Power on')
        self._handle_power_on()

    @abstractmethod
    def _handle_power_on(self):
        '''Implement power on logic'''

    def off(self):
        '''Turn off the power control'''
        self.log(f'{str(self)}: Power off')
        self._handle_power_off()

    @abstractmethod
    def _handle_power_off(self):
        '''Implement power off logic'''

    def reboot(self):
        self.off()
        self.log(f'{str(self)}: Waiting {self.reboot_delay}s to power on...')
        time.sleep(self.reboot_delay)
        self.on()
