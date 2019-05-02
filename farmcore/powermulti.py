import time
import re

from .powerbase import PowerBase


class PowerMulti(PowerBase):
    '''Combine multiple different power objects. Allows for more
    complex power sequences.'''

    def __init__(self, power_seq, reverse_off_seq=True):
        if not isinstance(power_seq, list):
            power_seq = [power_seq]

        self.power_seq = power_seq
        self.reverse_off_seq = reverse_off_seq

        self.on_seq = self._build_sequence('on')
        self.off_seq = self._build_sequence('off')

    @property
    def reboot_delay(self):
        return max(
            [p.reboot_delay for p in self.power_seq if isinstance(p, PowerBase)])

    def _build_sequence(self, method):
        seq = []
        regex_str = '[0-9]+\.*[0-9]*m{0,1}s'
        for p in self.power_seq:
            if isinstance(p, PowerBase):
                seq.append(getattr(p, method))
            elif (isinstance(p, str) and
                    re.match(regex_str, p)):
                seq.append(p)
            else:
                raise AttributeError('Invalid power seqence val [{}]'.format(
                    p))

        return seq

    def _do_sequence(self, seq):
        for action in seq:
            if callable(action):
                action()
            if isinstance(action, str):
                if action.endswith('ms'):
                    time.sleep(float(action[:-2])/1000)
                elif action.endswith('s'):
                    time.sleep(float(action[:-1]))

    def on(self):
        self._do_sequence(self.on_seq)

    def off(self):
        if self.reverse_off_seq:
            self._do_sequence(self.off_seq[::-1])
        else:
            self._do_sequence(self.off_seq)
