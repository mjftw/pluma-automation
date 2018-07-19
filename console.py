#!/usb/bin/env python3

import sys
import time
import pexpect
import pexpect.fdpexpect

from farmclass import Farmclass


DEFAULT_PROMPT = r'>>FARM>>'

class TimeoutNoRecieve(Exception):
    pass


class TimeoutNoRecieveStop(Exception):
    pass


class SubclassException(Exception):
    pass


class Console(Farmclass):
    """ Impliments the console functionality not specific to a given transport layer """
    def __init__(self, linesep, encoding='ascii'):
        if type(self) is Console:
            raise SubclassException(
                "Class is a base class and must be inherited")
        self._check_attr('_pex')

        self.encoding = encoding
        self.linesep = linesep

    def _check_attr(self, attr):
        if not hasattr(self, attr):
            raise SubclassException(
                "Variable '{}' must be created by inheriting class".format(
                    attr))

    def _err_must_override(self):
        raise SubclassException(
            "This function must be overridden by an inheriting class")

    @property
    def is_open(self):
        """ Check if the transport layer is ready to send and recieve"""
        self._err_must_override()

    @property
    def bytes_recieved(self):
        """ Return the number of bytes in the recieve buffer """
        self._err_must_override()

    def flush(self):
        """ Clear input buffer """
        self._err_must_override()

    def open(self):
        """ Open transport layer. E.g. Open serial port """
        self._err_must_override()

    def close(self):
        """ Close transport layer """
        self._err_must_override()

    @property
    def last_match(self):
        return self._pex.after

    def flush(self):
        return self._pex.read()

    def decode(self, text):
        return text.decode(self.encoding)

    def wait_for_data(self, timeout=10.0, sleep_time=0.1,
                      match=None, start_bytes=None):
        if not self.is_open:
            self.open()

        if match:
            if not isinstance(match, list):
                match = [match]
            expects = [pexpect.TIMEOUT, pexpect.EOF] + match

        if start_bytes is None:
            start_bytes = self.bytes_recieved

        elapsed = 0.0

        while(elapsed <= timeout):
            current_bytes = self.bytes_recieved

            self.log("Waiting for data: {} Waited[{:.1f}/{:.1f}s] Recieved[{:.0f}B]...".format(
                match, elapsed, timeout, current_bytes-start_bytes
                ))

            if match:
                if self._pex.expect(expects) > 1:
                    return True
            elif current_bytes > start_bytes:
                return True

            time.sleep(sleep_time)
            elapsed += sleep_time

        raise TimeoutNoRecieve('Timeout waiting to recieve data')
        return False

    def wait_for_quiet(self, timeout=10.0, quiet=0.3, sleep_time=0.1):
        if not self.is_open:
            self.open()

        last_bytes = self.bytes_recieved
        start_byes = last_bytes
        time_quiet = 0.0
        elapsed = 0.0

        while(elapsed <= timeout):
            current_bytes = self.bytes_recieved

            if current_bytes == last_bytes:
                time_quiet += sleep_time
            else:
                time_quiet = 0

            self.log("Waiting for quiet... Waited[{:.1f}/{:.1f}s] Quiet[{:.1f}/{:.1f}s] Recieved[{:.0f}B]...".format(
                elapsed, timeout, time_quiet, quiet, current_bytes-start_byes
                ))

            if time_quiet > quiet:
                return True

            last_bytes = current_bytes

            time.sleep(sleep_time)
            elapsed += sleep_time

        raise TimeoutNoRecieveStop('Timeout waiting for quiet')
        return False

    def send(self,
             cmd,
             recieve=False,
             match=None,
             ):
        if not self.is_open:
            self.open()
        if not self.is_open:
            raise RuntimeError("Could not open device")

        result = None

        if not recieve:
            self._pex.sendline(cmd)
        else:
            self.wait_for_quiet()
            self.flush()
            self._pex.sendline(cmd)
            if match:
                self.wait_for_data(match=match)
                result = self._pex.before
            else:
                self.wait_for_quiet()
                result = self.flush()

        return result

    def check_responds(self, timeout=10.0):
        start_bytes = self.bytes_recieved
        self.send("")
        return self.wait_for_data(timeout=timeout, start_bytes=start_bytes)

    def bash_change_prompt(self, prompt):
        self.send("export PS1='{}'".format(prompt))
        self.wait_for_quiet()
        self.flush()

    def bash_set_echo(self, echo):
        if echo:
            self.send('stty echo')
        else:
            self.send('stty -echo')
