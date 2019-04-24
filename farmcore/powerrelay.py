import time

from .baseclasses import PowerBase, RelayBase


# FIXME: We no longer have a reference to the Relay. Fix this.
class PowerRelay(PowerBase, RelayBase):
    def __init__(self, on_seq, off_seq):
        self.on_seq = on_seq
        self.off_seq = off_seq

    def _do_sequence(self, seq):
        for action in seq:
            if isinstance(action, tuple):
                self.toggle(action[0], action[1])
            if isinstance(action, str):
                if action.endswith('ms'):
                    time.sleep(float(action[:-2])/1000)
                elif action.endswith('s'):
                    time.sleep(float(action[:-1]))

    def on(self):
        self._do_sequence(self.on_seq)

    def off(self):
        self._do_sequence(self.off_seq)

    def reboot(self):
        self.off()
        self.on()
