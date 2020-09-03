import json
import os

from farmcore import Board, SerialConsole, SSHConsole, SoftPower, IPPowerPDU
from farmcore.baseclasses import Logger
from farmcli import Configuration, ConfigurationError, TargetConfigError

log = Logger()


class Credentials:
    def __init__(self, login=None, password=None):
        self.login = login
        self.password = password


class TargetConfig:
    @staticmethod
    def create_board(config):
        try:
            board = TargetConfig.__create_board(config)
        except ConfigurationError as e:
            raise TargetConfigError(e)
        else:
            TargetConfig.print_board_settings(board)
            return board

    @staticmethod
    def __create_board(config: Configuration) -> Board:
        credentials = TargetFactory.parse_credentials(
            config.pop('credentials'))

        serial, ssh = TargetFactory.create_consoles(
            config.pop('console'), credentials)

        if not serial and not ssh:
            log.warning("No console defined in the device configuration file")

        power = TargetFactory.create_power_control(
            config.pop('power'), ssh)

        config.ensure_consumed()
        return Board('Test board', console={'serial': serial, 'ssh': ssh}, power=power,
                     login_user=credentials.login, login_pass=credentials.password)

    @staticmethod
    def print_board_settings(board: Board):
        log.log('Components:', bold=True)

        serial = board.get_console('serial')
        suffix = 'Default' if serial and board.console is serial else None
        TargetConfig.print_component('Serial', serial, suffix)

        ssh = board.get_console('ssh')
        suffix = 'Default' if ssh and board.console is ssh else None
        TargetConfig.print_component('SSH', ssh, suffix)

        TargetConfig.print_component('Power control', board.power)
        TargetConfig.print_component('Storage', board.storage)
        TargetConfig.print_component('USB Hub', board.hub)
        log.log('')

    @staticmethod
    def print_component(label: str, component, suffix: str = None):
        color = 'green' if component else None
        if suffix:
            log.log(f'    {label}:  {str(component)} - {suffix}', color=color)
        else:
            log.log(f'    {label}:  {str(component)}', color=color)


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
        if not power_config:
            power_config = Configuration()

        POWER_SOFT = 'soft'
        POWER_IPPOWER9258 = 'ippower9258'
        POWER_LIST = [POWER_SOFT, POWER_IPPOWER9258]

        if len(power_config) > 1:
            raise TargetConfigError(
                'Only one power control should be provided in the target configuration,'
                f' but two or more provided:{os.linesep}{power_config}')

        control_type = POWER_SOFT
        if len(power_config) > 0:
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
