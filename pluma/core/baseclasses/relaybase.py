from abc import ABC, abstractmethod

from .hardwarebase import HardwareBase


class RelayBase(HardwareBase, ABC):

    def toggle(self, port: int, throw: str):
        '''Toggle relay'''
        self.log(f'{str(self)}: Switching port {port} to {throw}')
        self._handle_toggle(port, throw)

    @abstractmethod
    def _handle_toggle(self, port: int, throw: str):
        '''Implement toggle logic'''
