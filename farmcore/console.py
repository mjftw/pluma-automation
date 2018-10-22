#!/usb/bin/env python3

import sys
import time
import pexpect
import pexpect.fdpexpect

from .farmclass import Farmclass


DEFAULT_PROMPT = r'>>FARM>>'


class TimeoutNoRecieve(Exception):
    pass


class TimeoutNoRecieveStop(Exception):
    pass


class SubclassException(Exception):
    pass


class Console(Farmclass):
    """ Impliments the console functionality not specific to a given transport layer """
    def __init__(self, encoding='ascii'):
        if type(self) is Console:
            raise SubclassException(
                "Class is a base class and must be inherited")
        self._check_attr('_pex')

        self.encoding = encoding
        self._buffer = ''

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

    def open(self):
        """ Open transport layer and create _pex object. E.g. Open serial port """
        self._err_must_override()

    def close(self):
        """ Close transport layer """
        self._err_must_override()

    def flush(self, clear_buf=False):
        if not self.is_open:
            self.open()
        try:
            while 1:
                last_read = self.decode(self._pex.read_nonblocking(1, 0.01))
                self._buffer += last_read
        except pexpect.exceptions.TIMEOUT:
            pass
        except pexpect.exceptions.EOF:
            pass

        if clear_buf:
            self._buffer = ''
        return self._buffer

    @property
    def _buffer_size(self):
        return len(self._buffer)

    def _flush_get_size(self):
        self.flush(True)
        return self._buffer_size

    def decode(self, text):
        return text.decode(self.encoding, 'replace')

    def encode(self, text):
        return text.encode(self.encoding)

    def wait_for_data(self, timeout=10.0, sleep_time=0.1,
                      match=None, start_bytes=None, verbose=True):
        if not self.is_open:
            self.open()

        if match:
            if not isinstance(match, list):
                match = [match]
            expects = [pexpect.TIMEOUT, pexpect.EOF] + match
        else:
            self.flush()
            if start_bytes is None:
                start_bytes = self._flush_get_size()

        elapsed = 0.0

        while(elapsed <= timeout):
            if match:
                if verbose:
                    self.log("Waiting for pattern [{}]: Waited[{:.1f}/{:.1f}s]...".format(
                        match, elapsed, timeout))
                matched = expects[self._pex.expect(expects)]
                if matched in match:
                    return matched
            else:
                current_bytes = self._flush_get_size()
                if verbose:
                    self.log("Waiting for data: Waited[{:.1f}/{:.1f}s] Recieved[{:.0f}B]...".format(
                        elapsed, timeout, current_bytes-start_bytes))
                if current_bytes > start_bytes:
                    return True

            time.sleep(sleep_time)
            elapsed += sleep_time

        return False

    def wait_for_quiet(self, timeout=10.0, quiet=0.3, sleep_time=0.1, verbose=True):
        if not self.is_open:
            self.open()

        time_quiet = 0.0
        elapsed = 0.0

        last_bytes = 0

        while(elapsed <= timeout):
            current_bytes = self._flush_get_size()

            if current_bytes == last_bytes:
                time_quiet += sleep_time
            else:
                time_quiet = 0

            if verbose:
                self.log("Waiting for quiet... Waited[{:.1f}/{:.1f}s] Quiet[{:.1f}/{:.1f}s] Recieved[{:.0f}B]...".format(
                    elapsed, timeout, time_quiet, quiet, current_bytes
                    ))

            if time_quiet > quiet:
                return True

            last_bytes = self._flush_get_size()

            time.sleep(sleep_time)
            elapsed += sleep_time

        return False

    def send(self,
             cmd=None,
             recieve=False,
             match=None,
             log_recieved_on_pass=False,
             log_recieved_on_fail=False,
             log_verbose=True,
             timeout=-1,
             sleep_time=-1
             ):
        if not self.is_open:
            self.open()
        if not self.is_open:
            raise RuntimeError("Could not open device")

        if log_verbose:
            self.log("Sending command:\n{}".format(cmd))

        if not cmd:
            cmd=""

        if isinstance(cmd, str):
            cmd = self.encode(cmd)

        recieved = None
        matched = False

        """ Assign default timeout and sleep values if unassigned """
        data_timeout = timeout if timeout >= 0 else 30
        quiet_timeout = timeout if timeout >= 0 else 3
        data_sleep = sleep_time if sleep_time >= 0 else 1.0
        quiet_sleep = sleep_time if sleep_time >= 0 else 1.0

        if not recieve:
            self._pex.sendline(cmd)
            return (None, None)
        else:
            self.flush(True)
            self._pex.sendline(cmd)
            if match:
                matched = self.wait_for_data(
                    timeout=data_timeout,
                    sleep_time=data_sleep,
                    match=match,
                    verbose=log_verbose)
                recieved = self.decode(self._pex.before)
                if (matched and log_recieved_on_pass or
                        not matched and log_recieved_on_fail):
                    self.log("Command result:\n{}".format(result))
                return (recieved, matched)
            else:
                self.wait_for_quiet(
                    timeout=quiet_timeout,
                    sleep_time=quiet_sleep,
                    verbose=log_verbose)
                recieved = self._buffer
                return (recieved, None)

    def check_alive(self, timeout=10.0):
        start_bytes = self._flush_get_size()
        self.send("")
        alive = self.wait_for_data(timeout=timeout, start_bytes=start_bytes)
        if alive:
            self.log("Got response from: {}".format(self))
        else:
            self.log("No response from: {}".format(self))
        return alive

    def bash_change_prompt(self, prompt):
        self.send("export PS1='{}'".format(prompt))
        self.wait_for_quiet()
        self.flush(True)

    def bash_set_echo(self, echo):
        if echo:
            self.send('stty echo')
        else:
            self.send('stty -echo')
