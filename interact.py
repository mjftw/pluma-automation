#!/usb/bin/env python3

import time
import sys,os
import serial
import pexpect
import pexpect.fdpexpect as pfd
import re
from pprint import pprint as pp

default_prompt = r'^.*# '


def rec(s):
    if not isinstance(s, bytes):
        s = s.encode('ascii')
    return re.compile(s, re.MULTILINE)


class pexfuncs():

    def wait_for_quiet(self, maxtimeout=100):
        prompts = [pexpect.TIMEOUT]
        timeout = maxtimeout
        b1 = 0
        exit_count = 0
        quiet_count = 3

        while 1:

            self.log("Waiting for quiet. Timeout[{}] Quiet[{}] Bytes[{}]....".format(
                timeout, quiet_count - exit_count,
                self.bytes
                ))

            if timeout == 0:
                raise RuntimeError('Timeout waitin for quiet')

            if self.expect(prompts) != 0:
                raise RuntimeError("Bad value for self.expect")

            if self.bytes - b1 == 0:
                exit_count += 1
            else:
                exit_count = 0

            if exit_count == quiet_count:
                return 0

            b1 = self.bytes
            timeout -= 1

    def waitre(self, recvs, maxtimeout=100):

        timeout = 0

        if not isinstance(recvs, list):
            recvs = [recvs]

        prompts = [pexpect.TIMEOUT] + recvs

        self.log("Waiting for text {}".format([r.pattern for r in recvs]))

        while 1:
            #self.log("EXPECT[{}]>>> {}".format( self.bytes, prompts[2:] ))
            r = self.expect(prompts)
            if r >= 1:
                return True
            else:
                timeout += 1
                if timeout > maxtimeout:
                    raise RuntimeError('Timed out waiting for string {}'.format(str(recvs)))
                self.log("TIMEOUT {}/{} Bytes[{}] {}".format(
                    timeout, maxtimeout, self.bytes, [r.pattern for r in recvs]))

    def waitr(self, recvs, maxtimeout=100):

        if isinstance(recvs, str):
            recvs = [recvs]

        return self.waitre([rec(r) for r in recvs], maxtimeout)

    def send_newline(self):
        self.send(self.linesep)

    # Send, dont care about receive
    def snr(self, send):

        if isinstance(send, str):
            send = send.encode('ascii')

        self.log("SNR: [{}]".format(send))
        self.send(send)

    def echo_off(self, prompt=default_prompt):
        return self.psr('stty -echo', prompt=prompt)

    def validate_prompt(self, prompt=default_prompt):

        # Flush everything out first
        self.flush()

        # Send a newline
        self.send_newline()
        self.send_newline()
        self.send_newline()

        self.waitre(rec(prompt), maxtimeout=3)
        self.flush()

    # Prompt, send, receive
    def psr(self,
            send,
            escape = True,
            echo = False,
            maxtimeout = 5,
            prompt = default_prompt,
            after_prompt = None,
            send_only = False,
            unimode = 'ignore'):

        if isinstance(send, str):
            send = send.encode('ascii')

        # First, validate the current prompt
        self.validate_prompt(prompt)

        self.log("PSR: Issue command [{}]".format(send))

        # Send out the command
        self.send(send)
        self.send_newline()

        if send_only:
            return

        prompts = [pexpect.EOF, pexpect.TIMEOUT]

        if after_prompt is None:
            after_prompt = prompt

        prompts.append(rec(after_prompt))
        timeout = 0

        # WARNING:
        # Serial comms can sometimes generate bad values and the UnicodeDecode exception
        # will appear! So we default to ignoring the bad values, but sometimes it might
        # be useful to resend the command.
        while 1:
            r = self.expect(prompts)

            if r == 2:
                # Read all the data before the next prompt
                break

            elif r == 1:
                timeout += 1
                if timeout > maxtimeout:
                    raise RuntimeError('PSR Timed out waiting for repsonse')
                self.log("TIMEOUT {}/{} Bytes[{}] Reponse to [{}]".format(
                    timeout, maxtimeout, self.bytes, send))

        ret = self.before

        # If the original command is echoed ( usual in interactive shells ) then
        # we strip it out here first.
        if echo:
            # We use re.match() assuming that the echo reply is always at the start
            d = re.match(send, ret)

            # No match?
            if d is None:
                raise RuntimeError("Echo mode failed to find original command {}".format(send))

            ret = d.string[d.end():]

        self.log("Command [{}] Reponds with [{}]".format(send, ret[:20]))

        return ret.decode('utf-8', unimode).strip()


class serialSpawn(pfd.fdspawn, pexfuncs):

    def __init__(self, filename, board,  *args, **kw):
        self.bytes = 0
        self.board = board
        self.log("Initialise serSpawn at {}".format(filename))
        self.ser = self.try_init_serial(filename)
        return super().__init__(self.ser.fileno(), *args, timeout=5, **kw)

    def log(self, s):
        self.board.log(s)

    def __repr__(self):
        return "PExpect Serial at {} for board {}".format(self.ser.port, self.board)

    def try_init_serial(self, filename, timeout=1):
        for _ in range(10):
            try:
                s = serial.Serial(filename, 115200, timeout=timeout)
                return s
            except Exception as e:
                self.log("Failed to init serial ({}), Error - [{}].  trying again.".format(filename, e))
                time.sleep(1)

        raise IOError('Cannot start board and connect to serial')

    def read(self, *a, **kw):
        self.log("Blocking read...")
        return super().read(*a, **kw)

    def read_nonblocking(self, size=1, timeout=0):
        # NOTE: This is the serial INTERNAL timeout, we keep this small and the pexpect
        # modules deals nicely with the higher-level timeout
        # self.ser.timeout = 1
        b = self.ser.read(size)
        self.bytes += len(b)
        self._log(b, 'read')
        return b

    def flush(self):
        self.buffer = bytes()
        self.ser.reset_input_buffer()

    def close(self):
        self.ser.flush()
        return self.ser.close()

    def send(self, s):
        if isinstance(s, str):
            s = s.encode('ascii')
        return self.ser.write(s)


class genSpawn(pexpect.spawn, pexfuncs):

    bytes = 0

    def log(self, s):
        pass
