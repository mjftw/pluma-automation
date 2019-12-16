from ..baseclasses import PowerBase


class PowerMock(PowerBase):
    def __init__(self, reboot_delay=None):
        PowerBase.__init__(self, reboot_delay)

    def on(self):
        self.log('Mock method called: on()')

    def off(self):
        self.log('Mock method called: off()')
