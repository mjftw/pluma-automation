import json
import logging

from farmcore import Board, SerialConsole, SSHConsole, SoftPower, IPPowerPDU
from farmcli import PlumaLogger, Configuration, ConfigurationError

log = PlumaLogger()


class TargetConfigError(Exception):
    pass


class Credentials:
    def __init__(self, login=None, password=None):
        self.login = login
        self.password = password


class TargetConfig:
    @staticmethod
    def create_board(config):
        try:
            credentials = TargetFactory.parse_credentials(
                config.pop('credentials'))

            serial, ssh = TargetFactory.create_consoles(
                config.pop('console'), credentials)
            main_console = serial or ssh

            power = TargetFactory.create_power_control(
                config.pop('power'), main_console)

            log.log('Components:', bold=True)
            more_info = '- Default' if serial and main_console == serial else ''
            log.log(f'    Serial:         {str(serial)} {more_info}',
                    color='green' if serial else 'normal')
            more_info = '- Default' if ssh and main_console == ssh else ''
            log.log(f'    SSH:            {str(ssh)} {more_info}',
                    color='green' if ssh else 'normal')
            log.log(f'    Power control:  {str(power)}',
                    color='green' if power else 'normal')
            log.log('')

            config.ensure_consumed()
            board = Board('Test board', console=main_console, power=power,
                          login_user=credentials.login, login_pass=credentials.password)
        except ConfigurationError as e:
            raise TargetConfigError(e)

        return board


class TargetFactory:
    @staticmethod
    def parse_credentials(credentials_config):
        if not credentials_config:
            return Credentials()

        credentials = Credentials(
            credentials_config.pop('login'),
            credentials_config.pop('password'))
        credentials_config.ensure_consumed()
        return credentials

    @staticmethod
    def create_consoles(config, credentials):
        if not config:
            return None, None

        serial = TargetFactory.create_serial(config.pop('serial'))
        ssh = TargetFactory.create_ssh(config.pop('ssh'), credentials)
        config.ensure_consumed()
        return serial, ssh

    @staticmethod
    def create_serial(serial_config):
        if not serial_config:
            return None

        log.debug(f'Serial config = {serial_config}')

        port = serial_config.pop('port')
        if not port:
            raise TargetConfigError(
                'Missing "port" attributes for serial console in the configuration file')

        serial = SerialConsole(port, int(serial_config.pop('baud') or 115200))
        serial_config.ensure_consumed()
        return serial

    @staticmethod
    def create_ssh(ssh_config, credentials):
        if not ssh_config:
            return None

        log.debug('SSH config = ' + json.dumps(ssh_config.content()))
        target = ssh_config.pop('target')
        login = ssh_config.pop('login', credentials.login)

        if not target or not login:
            raise TargetConfigError(
                'Missing "target" or "login" attributes for SSH console in the configuration file')

        password = ssh_config.pop('password', credentials.password)
        ssh_config.ensure_consumed()
        return SSHConsole(target, login, password)

    @staticmethod
    def create_power_control(power_config, console):
        POWER_SOFT = 'soft'
        POWER_IPPOWER9258 = 'ippower9258'
        POWER_LIST = [POWER_SOFT, POWER_IPPOWER9258]

        if power_config.len() > 1:
            raise TargetConfigError(
                f'Only one power control should be provided in the target configuration, but two or more provided:\n{power_config}')

        control_type = POWER_SOFT
        if power_config.len() > 0:
            control_type = power_config.first()

        if control_type not in POWER_LIST:
            raise TargetConfigError(
                f'Unsupported power control type "{control_type}". Supported types: {POWER_LIST}')

        power_config = power_config.pop(control_type) or Configuration()
        power = None
        if control_type == POWER_SOFT:
            if not console:
                raise TargetConfigError(
                    'No console available for soft power control')

            power = SoftPower(console)

        elif control_type == POWER_IPPOWER9258:
            host = power_config.pop('host')
            outlet = power_config.pop('outlet')
            if not host or not outlet:
                raise TargetConfigError(
                    'IP Power PDU "host" and/or "outlet" attributes are missing')

            port = power_config.pop('port')
            login = power_config.pop('login')
            password = power_config.pop('password')
            power = IPPowerPDU(outlet, host, netport=port,
                               username=login, password=password)
        else:
            raise Exception('Unreachable, unknown power controller')

        power_config.ensure_consumed()
        return power
