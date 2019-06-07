from .farmclass import Farmclass
import time


class PowerBase(Farmclass):
    def __init__(self, reboot_delay=None):
        self.reboot_delay = reboot_delay or 0.5

        if type(self) is PowerBase:
            raise AttributeError(
                'This is a base class, and must be inherited')

    def on(f):
        def wrap(self, *args, **kwargs):
            self.log(f'{str(self)}: Power on')
            f(self, *args, **kwargs)
        return wrap

    def off(f):
        def wrap(self, *args, **kwargs):
            self.log(f'{str(self)}: Power off')
            f(self, *args, **kwargs)
        return wrap

    def reboot(self):
        self.off()
        self.log(f'{str(self)}: Waiting {self.reboot_delay}s to power on...')
        time.sleep(self.reboot_delay)
        self.on()

    def __bool__(self):
        ''' Base class is falsey. Must inherit'''
        return True if type(self) is not PowerBase else False
