#!/usr/bin/env python3
""" The APC is a switched rack PDU which controlls whether a board is powered """
import sys
import time
import pexpect.exceptions as pex

from .farmclass import Farmclass
from .telnetconsole import TelnetConsole
from .console import CannotOpen, LoginFailed
from .powerbase import PowerBase


class NoAPC(Exception):
    pass


class InvalidPort(Exception):
    pass


class APC(Farmclass, PowerBase):
    def __init__(self, host, username, password, port):
        self.host = host
        self.username = username
        self.password = password

        if 1 <= port <= 8:
            self.port = port
        else:
            raise InvalidPort("Invalid port[{}]").format(port)

        self.console = TelnetConsole(self.host)

    def _login(self):
        e = None
        for _ in range(1, 5):
            try:
                self.console.open()
                e = None
            except CannotOpen as ex:
                e = ex
                self.log('WARNING: Failed to gain control of APC console. Is it in use?')
                self.log('Sleeping 1 second and retrying...')
                time.sleep(1)

        if e:
            raise e

        for _ in range(1, 5):
            try:
                self.console.login(
                    username=self.username,
                    password=self.password,
                    username_match='User Name',
                    password_match='Password',
                    success_match='Control Console'
                )
                return
            except LoginFailed as ex:
                e = ex
                self.log('WARNING: Failed to log in')
                self.log('Sleeping 1 second and retrying...')
                time.sleep(1)

        raise e

    def _disconnect(self):
        if self.console.is_open:
            self.console.send('\x03', match='Control Console')
            self.console.send('4', match='Connection Closed')

    def _switch(self, state):
        if state not in ['on', 'off']:
            raise RuntimeError('Invalid state! Expected "on" or "off"')

        self._login()

        self.console.send('1', match='Device Manager')
        self.console.send('2', match='Outlet Management')
        self.console.send('1', match='Outlet Control/Configuration')
        self.console.send(str(self.port), match='Outlet       : {}'.format(self.port))
        self.console.send('1', match='Control Outlet')
        self.console.send('1' if state == 'on' else '2', match="Enter 'YES' to continue")
        self.console.send('YES', match='Press <ENTER> to continue')
        self.console.send('', match='Control Outlet')

        self._disconnect()
        self.console.close()

    def on(self, dummy=None):
        self._switch('on')

    def off(self, dummy=None):
        self._switch('off')
