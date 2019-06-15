from ..baseclasses import PowerBase


class PowerMock(PowerBase):
    def __init__(self, reboot_delay=None):
        PowerBase.__init__(self, reboot_delay)

    @PowerBase.on
    def on(self):
        self.log('Mock method called: on()')

    @PowerBase.off
    def off(self):
        self.log('Mock method called: off()')
