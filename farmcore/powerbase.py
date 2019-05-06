import time

class PowerBase():
    reboot_delay = 0.5

    def on(self):
        raise NotImplemented('This method must be implimented by inheriting class')

    def off(self):
        raise NotImplemented('This method must be implimented by inheriting class')

    def reboot(self):
        self.off()
        time.sleep(self.reboot_delay)
        self.on()
