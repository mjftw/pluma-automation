#!/usr/bin/env python3
""" The APC is a switched rack PDU which controlls whether a board is powered """
import interact
import sys
import time
import pexpect.exceptions as pex


class NoAPC(Exception):
    pass


class InvalidPort(Exception):
    pass


class APC():
    def __init__(self, host, user, pw, port):
        self.host = host
        self.user = user
        self.pw = pw
        self.spawn = None
        if 1 <= port <= 8:
            self.index = port - 1
        else:
            raise InvalidPort("Invalid port[{}]").format(port)

    def __repr__(self):
        return "\n[APC: host={}, user={}, pw={}, port={}, spawn={}]".format(
            self.host, self.user, self.pw, self.index+1, self.spawn
        )

    def _init_spawn(self):
        if not self.spawn:
            cl = "telnet {}".format(self.host)
            for _ in range(5):
                self.spawn = interact.genSpawn(
                    cl, logfile=open('/tmp/apclog', 'ab'), timeout=5)
                self.spawn.linesep = '\r\n'.encode('ascii')

                try:
                    # This can get to EOF which in this instance means that the
                    # telnet sesssion has gone away. This is USUALLLY becuase only
                    # one user can _login at a time but it could be something else.
                    self._login()
                except pex.EOF:
                    print("Warning - APC Blocked. Waiting then trying again...")
                    time.sleep(2)
                else:
                    return

            raise IOError("Couldn't connect to APC.")

    def _login(self):
        self.spawn.waitr('User Name')
        self.spawn.snr(self.user)
        self.spawn.send_newline()
        self.spawn.waitr('Password')
        self.spawn.snr(self.pw)
        self.spawn.send_newline()

    def _disconnect(self):
        if self.spawn:
            self.spawn.sendcontrol('c')
            self.spawn.waitr('^> ')
            self._send(4)
            self.spawn.close(force=True)
            self.spawn = None

    def _send(self, s):
        self.spawn.waitr('^> ')
        self.spawn.snr(str(s))
        self.spawn.send_newline()

    def menu(self, l):
        for e in l:
            self._send(e)

    def on(self, dummy=None):
        self._init_spawn()
        self.menu([1, 2, 1, self.port, 1, 1])
        self.spawn.snr('YES')
        self.spawn.send_newline()
        self.spawn.send_newline()
        self.spawn.waitr('^> ')
        self._disconnect()

    def off(self, dummy=None):
        self._init_spawn()
        self.menu([1, 2, 1, self.port, 1, 2])
        self.spawn.snr('YES')
        self.spawn.send_newline()
        self.spawn.send_newline()
        self.spawn.waitr('^> ')
        self._disconnect()


def get_apc(apcs, host, port):
    for apc in apcs:
        if apc.index+1 == port and apc.host == host:
            return apc

    raise NoAPC("Can't find APC with host[{}], port[{}]".format(
        host, port))
