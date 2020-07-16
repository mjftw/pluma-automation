import json
import logging

from farmcore import Board, SerialConsole, HostConsole, SoftPower, IPPowerPDU
from farmcli import PlumaLogger, Configuration, ConfigurationError

log = PlumaLogger.logger()


class TargetConfigError(Exception):
    pass


class TargetConfig:
    @staticmethod
    def create_board(config):
        try:
            serial, ssh = TargetFactory.create_consoles(config.pop('console'))
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
            board = Board('Test board', console=main_console, power=power)
        except ConfigurationError as e:
            raise TargetConfigError(e)

        return board


class TargetFactory:
    @staticmethod
    def create_consoles(config):
        if not config:
            return None, None

        serial = TargetFactory.create_serial(config.pop('serial'))
        ssh = TargetFactory.create_ssh(config.pop('ssh'))
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
    def create_ssh(ssh_config):
        if not ssh_config:
            return None

        log.debug('SSH config = ' + json.dumps(ssh_config.content()))
        target = ssh_config.pop('target')
        login = ssh_config.pop('login')

        if not target or not login:
            raise TargetConfigError(
                'Missing "target" or "login" attributes for SSH console in the configuration file')

        password = ssh_config.pop('password')
        command = ''
        if not password:
            command = f'ssh {login}@{target} -o StrictHostKeyChecking=no'
        else:
            command = f'sshpass -p {password} ssh {login}@{target} -o PreferredAuthentications=password -o PubkeyAuthentication=no -o StrictHostKeyChecking=no'

        log.debug(f'SSH connection command = "{command}"')
        ssh_config.ensure_consumed()
        return HostConsole(command)

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
