class PowerBase():
    def on(self):
        raise NotImplemented('This method must be implimented by inheriting class')

    def off(self):
        raise NotImplemented('This method must be implimented by inheriting class')

    def reboot(self):
        self.off()
        self.on()