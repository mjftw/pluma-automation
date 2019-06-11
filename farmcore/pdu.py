import time
import requests
import re

from .telnetconsole import TelnetConsole
from .exceptions import ConsoleCannotOpen, ConsoleLoginFailed
from .baseclasses import PowerBase


class PDUError(Exception):
    pass


class PDUInvalidPort(PDUError):
    pass


class PDURequestError(PDUError):
    pass


class IPPowerPDU(PowerBase):
    ''' IP Power 9258 is a PDU which can respond to http requests '''
    def __init__(self, port,
            host=None, netport=None, username=None, password=None,
            interface=None, interface_ip=None, reboot_delay=None):
        if 1 <= port <= 4:
            self.port = port
        else:
            raise PDUInvalidPort("Invalid port[{}]").format(port)

        self.host = host or '192.168.1.100'
        self.netport = netport or 80
        self.username = username or 'admin'
        self.password = password or '12345678'
        self.interface = interface
        self.interface_ip = interface_ip or '192.168.1.110'

        PowerBase.__init__(self, reboot_delay)

    @PowerBase.on
    def on(self):
        self._make_request('cmd=setpower+p6{}=1'.format(self.port))

    @PowerBase.off
    def off(self):
        self.log(f'{str(self)}: Power off...')
        self._make_request('cmd=setpower+p6{}=0'.format(self.port))

    def is_on(self):
        power_str_all = self._make_request('cmd=getpower')

        try:
            power_str = re.search(
                'p6{}=[01]'.format(self.port), power_str_all).group(0)

            if power_str[-1] == '1':
                return True
            elif power_str[-1] == '0':
                return False
        except (IndexError, AttributeError):
            raise PDURequestError('Invalid power state string [{}]'.format(
                power_str_all))

    def _make_request(self, params, max_tries=5):
        #E.g. http://192.168.1.100/set.cmd?user=admin&pass=12345678&cmd=setpower+p61=0

        if isinstance(params, list):
            params = '&'.join(params)

        params_str = '&'.join([
            'user=' + self.username,
            'pass=' + self.password,
            params
        ])

        url = 'http://{}:{}/set.cmd?{}'.format(
            self.host, self.netport, params_str)

        success = False
        exception = None
        for _ in range(0, max_tries):
            if success:
                break
            try:
                r = requests.get(url, timeout=3)
                success = True
            except requests.exceptions.Timeout as e:
                exception = e
                if (self.interface and
                        self.interface.ip_address != self.interface_ip):
                    self.log(str(e))
                    self.log(
                        'Setting interface address to {} and retrying...'.format(
                            self.interface_ip))
                    self.interface.set_ip_address(self.interface_ip)
                    self.interface.up()
                time.sleep(1)

        if not success:
            raise exception

        if r.status_code != 200:
            raise PDURequestError('Request failed. {}, Err[{}]'.format(
                r.text, r.status_code))

        return r.text

class APCPDU(PowerBase):
    """ The APC is a switched rack PDU which controls whether a board is powered """

    def __init__(self, host, username, password, port, reboot_delay=None):
        self.host = host
        self.username = username
        self.password = password

        if 1 <= port <= 8:
            self.port = port
        else:
            raise PDUInvalidPort("Invalid port[{}]").format(port)

        self.console = TelnetConsole(self.host)

        PowerBase.__init__(self, reboot_delay)


    def _login(self):
        e = None
        for _ in range(1, 5):
            try:
                self.console.open()
                e = None
            except ConsoleCannotOpen as ex:
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
            except ConsoleLoginFailed as ex:
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

    @PowerBase.on
    def on(self, dummy=None):
        self._switch('on')

    @PowerBase.off
    def off(self, dummy=None):
        self._switch('off')
