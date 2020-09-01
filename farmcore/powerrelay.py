import time

from .baseclasses import PowerBase, RelayBase


class PowerRelay(PowerBase):
    def __init__(self, relay, on_seq, off_seq, reboot_delay=None):
        if not isinstance(relay, RelayBase):
            raise TypeError('relay must be an instance of RelayBase')

        self.relay = relay
        self.on_seq = on_seq
        self.off_seq = off_seq

        PowerBase.__init__(self, reboot_delay)

        self.relay.console.log_echo = False

    def _do_sequence(self, seq):
        for action in seq:
            if isinstance(action, tuple):
                self.relay.toggle(action[0], action[1])
            if isinstance(action, str):
                if action.endswith('ms'):
                    time.sleep(float(action[:-2])/1000)
                elif action.endswith('s'):
                    time.sleep(float(action[:-1]))

    @PowerBase.on
    def on(self):
        self._do_sequence(self.on_seq)

    @PowerBase.off
    def off(self):
        self._do_sequence(self.off_seq)
