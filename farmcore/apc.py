#!/usr/bin/env python3

import sys
import time,threading
import pexpect.exceptions as pex
import os
import getpass
from farmcore.farm_base import FarmBase
from farmcore import interact

class APC(FarmBase):
    def __init__(self, host, user, pw, port=None, quiet=False):
        self.host = host
        self.user = user
        self.pw = pw
        self.quiet = quiet
        self.spawn = None
        self.log("Registered APC")
        self.lock = threading.Lock()

    def __repr__(self):
        return "APC[{}]".format( self.host )
    
    def init_spawn(self):
        if not self.spawn:
            cl = "telnet {}".format(self.host)
            for _ in range(5):
                self.spawn = interact.genSpawn(
                    cl, logfile=open('/tmp/apclog_{}'.format( getpass.getuser() ), 'ab'), timeout=5)
                self.spawn.linesep = '\r\n'.encode('ascii')

                try:
                    # This can get to EOF which in this instance means that the
                    # telnet sesssion has gone away. This is USUALLLY becuase only
                    # one user can login at a time but it could be something else.
                    self.login()
                except pex.EOF:
                    print("Warning - APC Blocked. Waiting then trying again...")
                    time.sleep(2)
                else:
                    return

            raise IOError("Couldn't connect to APC.")


    def __getitem__(self, index):
        return (self,index)

    def login(self):
        self.spawn.waitr('User Name')
        self.spawn.snr(self.user)
        self.spawn.send_newline()
        self.spawn.waitr('Password')
        self.spawn.snr(self.pw)
        self.spawn.send_newline()

    def send(self, s):
        self.spawn.waitr('^> ')
        self.spawn.snr(str(s))
        self.spawn.send_newline()

    def menu(self, l):
        for e in l:
            self.send(e)

    def on(self, index, dummy=None):
        self.lock.acquire()
        self.init_spawn()
        self.menu([1, 2, 1, index, 1, 1])
        self.spawn.snr('YES')
        self.spawn.send_newline()
        self.spawn.send_newline()
        self.spawn.waitr('^> ')
        self.disconnect()
        self.lock.release()

    def off(self, index, dummy=None):
        self.lock.acquire()
        self.init_spawn()
        self.menu([1, 2, 1, index, 1, 2])
        self.spawn.snr('YES')
        self.spawn.send_newline()
        self.spawn.send_newline()
        self.spawn.waitr('^> ')
        self.disconnect()
        self.lock.release()

    def disconnect(self):
        if self.spawn:
            self.spawn.sendcontrol('c')
            self.spawn.waitr('^> ')
            self.send(4)
            self.spawn.close(force=True)
            self.spawn = None


