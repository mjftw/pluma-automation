import time

from .usbrelay import USBRelay


class PowerRelay(USBRelay):
    def __init__(self, hub, on_seq, off_seq):
        USBRelay.__init__(self, hub)
        self.on_seq = on_seq
        self.off_seq = off_seq

    def restart(self):
        self.log("Rebooting")
        self.off()
        self.on()

    def do_sequence(self, seq):
        for action in seq:
            if isinstance(action, tuple):
                self.toggle(action[0], action[1])
            if isinstance(action, str):
                if action.endswith('ms'):
                    time.sleep(float(action[:-2])/1000)
                elif action.endswith('s'):
                    time.sleep(float(action[:-1]))

    def on(self):
        self.do_sequence(self.on_seq)

    def off(self):
        self.do_sequence(self.off_seq)
