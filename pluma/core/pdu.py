import time
import requests
import re
import json

from .telnetconsole import TelnetConsole
from .exceptions import ConsoleCannotOpenError, ConsoleLoginFailedError
from .baseclasses import PowerBase


class PDUError(Exception):
    pass


class PDUInvalidPort(PDUError):
    pass


class PDURequestError(PDUError):
    pass


class PDUReqestsBase():
    def __init__(self, interface=None, interface_ip=None):
        self.interface = interface
        self.interface_ip = interface_ip

        assert hasattr(self, 'host')
        assert hasattr(self, 'netport')
        assert hasattr(self, 'log')

    def _make_request(self, endpoint, params=None, method=None,
                      timeout=10, max_tries=1):
        if isinstance(params, list):
            params = '&'.join(params)

        method = method or 'GET'

        if method == 'GET':
            request_method = requests.get
        elif method == 'POST':
            request_method = requests.post
        else:
            raise PDURequestError(
                'Unsupported request method [{}]. Supported: {}'.format(
                    method, ['GET', 'POST']))

        url = 'http://{}{}{}{}'.format(
            self.host,
            ':' + str(self.netport) if self.netport else '',
            '/' + endpoint if endpoint else '',
            '?' + params if params else ''
        )

        success = False
        exception = None
        for _ in range(0, max_tries):
            if success:
                break
            try:
                r = request_method(url, timeout=timeout)
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


class EnergeniePDU(PowerBase, PDUReqestsBase):
    ''' Energenie MIHO005 Smart Plug with http request interface'''

    def __init__(self, host, socket, netport=None, interface=None,
                 interface_ip=None, reboot_delay=None):
        assert isinstance(socket, int) and socket >= 0

        self.host = host
        self.socket = socket
        self.netport = netport or 5000

        self._retries = 3

        PowerBase.__init__(self, reboot_delay)
        PDUReqestsBase.__init__(self, interface, interface_ip)

    @property
    def endpoint(self):
        return f'socket/{self.socket}'

    def get_info(self):
        json_info = self._make_request(
            endpoint=self.endpoint, timeout=30)
        return json.loads(json_info)

    @PowerBase.on
    def on(self):
        on = None
        for i in range(0, self._retries):
            self._make_request(endpoint=f'{self.endpoint}/on')
            on = self.is_on()
            if on:
                break
            else:
                self.error(f'Failed to turn on. Attempt {i+1}/{self._retries}')

        if not on:
            self.error('Failed to turn on', PDUError)

    @PowerBase.off
    def off(self):
        on = None
        for i in range(0, self._retries):
            self._make_request(endpoint=f'{self.endpoint}/off')
            on = self.is_on()
            if not on:
                break
            else:
                self.error(f'Failed to turn off. Attempt {i+1}/{self._retries}')

        if on:
            self.error('Failed to turn off', PDUError)

    def is_on(self):
        info = self.get_info()

        if 'state' not in info:
            raise PDURequestError('Reqest json text returned does not include "state"')

        return True if info['state'] else False


class IPPowerPDU(PowerBase, PDUReqestsBase):
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

        PowerBase.__init__(self, reboot_delay)
        PDUReqestsBase.__init__(self, interface, interface_ip or '192.168.1.110')

    def make_request(self, params: str) -> str:
        # E.g. http://192.168.1.100/set.cmd?user=admin&pass=12345678&cmd=setpower+p61=0
        params_str = '&'.join([
            'user=' + self.username,
            'pass=' + self.password,
            params
        ])
        return self._make_request(endpoint='set.cmd', params=params_str, max_tries=2)

    @PowerBase.on
    def on(self):
        self.make_request('cmd=setpower+p6{}=1'.format(self.port))

    @PowerBase.off
    def off(self):
        self.make_request('cmd=setpower+p6{}=0'.format(self.port))

    def is_on(self):
        power_str_all = self.make_request('cmd=getpower')

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
            except ConsoleCannotOpenError as ex:
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
            except ConsoleLoginFailedError as ex:
                e = ex
                self.log('WARNING: Failed to log in')
                self.log('Sleeping 1 second and retrying...')
                time.sleep(1)

        raise e

    def _disconnect(self):
        if self.console.is_open:
            self.console.send_and_expect('\x03', match='Control Console')
            self.console.send_and_expect('4', match='Connection Closed')

    def _switch(self, state):
        if state not in ['on', 'off']:
            raise RuntimeError('Invalid state! Expected "on" or "off"')

        self._login()

        self.console.send_and_expect('1', match='Device Manager')
        self.console.send_and_expect('2', match='Outlet Management')
        self.console.send_and_expect('1', match='Outlet Control/Configuration')
        self.console.send_and_expect(
            str(self.port), match='Outlet       : {}'.format(self.port))
        self.console.send_and_expect('1', match='Control Outlet')
        self.console.send_and_expect(
            '1' if state == 'on' else '2', match="Enter 'YES' to continue")
        self.console.send_and_expect('YES', match='Press <ENTER> to continue')
        self.console.send_and_expect('', match='Control Outlet')

        self._disconnect()
        self.console.close()

    @PowerBase.on
    def on(self):
        self._switch('on')

    @PowerBase.off
    def off(self):
        self._switch('off')
