#!/usb/bin/env python3

import sys
import time
import serial
import pexpect

from farmclass import Farmclass

DEFAULT_PROMPT = r'>>FARM>>'


class TimeoutNoRecieve(Exception):
    pass


class TimeoutNoRecieveStop(Exception):
    pass


class Console(Farmclass):
    linesep = '\r\n'

    def __init__(self, port, baud, timeout=100, prompt=DEFAULT_PROMPT):
        self.port = port
        self.timeout = timeout
        self.baud = baud
        self.bytes = 0
        self.prompt = prompt
        self._ser = serial.Serial()
        self._ser_pex = None

    @property
    def is_open(self):
        return self._ser.isOpen()

    @property
    def last_cmd_result(self):
        if self._ser_pex:
            return self._ser_pex.before
        else:
            return None

    def __repr__(self):
        return "Serial console device: {}".format(self._ser.port)

    def open(self):
        self.log("Trying to open serial port {}".format(self.port))
        for _ in range(10):
            try:
                self._ser = serial.Serial(
                    port=self.port,
                    baudrate=self.baud,
                    timeout=self.timeout
                )
                self._ser_pex = pexpect.fdpexpect.fdspawn(
                    fd=self._ser.fileno(), timeout=self.timeout)

                self.log("Init serial {} success".format(self.port))
                return
            except Exception as e:
                self.log("Failed to init serial ({}), Error -[{}]. Trying again.".format(self.port, e))
                time.sleep(1)

    def send_newline(self):
        self.send("")

    def close(self):
        if self.is_open:
            self._ser.flush()
            self._ser.close()
            self.log("Closed serial")
        else:
            self.log("Cannot close serial as it is not open")

    def flush(self):
        self._ser_pex.expect([pexpect.EOF, pexpect.TIMEOUT])
        self._ser.reset_input_buffer()

    def wait_for_recieve_stop(self, timeout=100):
        last_bytes = 0
        exit_count = 0
        quiet_count = 3

        while 1:
            self.log("Waiting for quiet. Timeout[{}] Quiet[{}] Bytes[{}]....".format(
                timeout, quiet_count - exit_count,
                self._ser.in_waiting
                ))

            if timeout <= 0:
                if last_bytes == 0:
                    raise TimeoutNoRecieve('Timeout waiting to recieve data')
                else:
                    raise TimeoutNoRecieveStop('Timeout waiting recieve to stop')

            if(self._ser.in_waiting - last_bytes == 0 and
                    self._ser.in_waiting > 0):
                exit_count += 1
            else:
                exit_count = 0

            if exit_count == quiet_count:
                return 0

            last_bytes = self._ser.in_waiting
            timeout -= 1
            time.sleep(0.1)

    def send(self, cmd, get_result=False, force_prompt=True):
        if not self.is_open:
            self.open()

        result = None

        if force_prompt:
            self._ser_pex.sendline("export PS1='{}'".format(self.prompt))
            self.wait_for_recieve_stop()

        if get_result:
            self.flush()

            self._ser_pex.sendline(cmd)
            expects = [self.prompt, pexpect.EOF, pexpect.TIMEOUT]

            self.wait_for_recieve_stop()

            if(self._ser_pex.expect(expects) != 0):
                raise RuntimeError('Did not find prompt {}'.format(
                    self.prompt))

            result = self.last_cmd_result

            if result:
                result = result.decode('ascii')
        else:
            self._ser_pex.sendline(cmd)

        return result

    def set_echo(self, echo):
        if echo:
            self.send('stty echo')
        else:
            self.send('stty -echo')
