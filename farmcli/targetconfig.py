import json
import logging

from farmcore import Board, SerialConsole, HostConsole, SoftPower
from farmcli import PlumaLogger

log = PlumaLogger.logger()


class TargetConfig:
    @staticmethod
    def create_board(config):
        serial, ssh = TargetFactory.create_consoles(config.get('console'))
        power = TargetFactory.create_power_control(config.get('power'), serial)
        main_console = serial or ssh

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

        board = Board('Test board', console=main_console, power=power)
        return board


class TargetFactory:
    @staticmethod
    def create_consoles(config):
        if not config:
            return None, None

        serial = TargetFactory.create_serial(config.get('serial'))
        ssh = TargetFactory.create_ssh(config.get('ssh'))
        return serial, ssh

    @staticmethod
    def create_serial(serial_config):
        if not serial_config:
            return None

        log.debug('Serial config = ' + json.dumps(serial_config))

        port = serial_config.get('port')
        if not port:
            raise ValueError(
                'Missing "port" attributes for serial console in the configuration file')

        return SerialConsole(port, int(serial_config.get('baud') or 115200))

    @staticmethod
    def create_ssh(ssh_config):
        if not ssh_config:
            return None

        log.debug('SSH config = ' + json.dumps(ssh_config))
        target = ssh_config.get('target')
        login = ssh_config.get('login')

        if not target or not login:
            raise ValueError(
                'Missing "target" or "login" attributes for SSH console in the configuration file')

        password = ssh_config.get('password')
        command = ''
        if not password:
            command = f'ssh {login}@{target} -o StrictHostKeyChecking=no'
        else:
            command = f'sshpass -p {password} ssh {login}@{target} -o PreferredAuthentications=password -o PubkeyAuthentication=no -o StrictHostKeyChecking=no'

        log.debug(f'SSH connection command: {command}')
        return HostConsole(command)

    @staticmethod
    def create_power_control(power_config, serial):
        if serial:
            return SoftPower(serial)
        else:
            return None
