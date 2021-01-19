import json
import os
from typing import Dict, Optional
from copy import deepcopy

from pluma import Board, SerialConsole, SSHConsole, SoftPower, IPPowerPDU
from pluma.cli import Configuration, ConfigurationError, TargetConfigError, \
    PlumaContext
from pluma.core.power import Uhubctl
from pluma.core.baseclasses import Logger, ConsoleBase, PowerBase
from pluma.core.dataclasses import SystemContext, Credentials

log = Logger()


class TargetConfig:
    @staticmethod
    def create_context(config: Configuration) -> PlumaContext:
        if not isinstance(config, Configuration):
            raise ValueError('Invalid configuration: The configuration passed '
                             'should be a Configuration instance.')
        try:
            context = TargetConfig._create_context(config)
        except ConfigurationError as e:
            raise TargetConfigError(e)
        else:
            TargetConfig.print_context_settings(context)
            config.ensure_consumed()
            return context

    @staticmethod
    def _create_context(config: Configuration) -> PlumaContext:
        variables = TargetFactory.parse_variables(
            config.pop_optional(Configuration, 'variables'))
        system = TargetFactory.parse_system_context(
            config.pop_optional(Configuration, 'system'))
        consoles = TargetFactory.create_consoles(
            config.pop_optional(Configuration, 'console'), system)

        serial = consoles.get('serial')
        ssh = consoles.get('ssh')
        if not serial and not ssh:
            log.warning("No console defined in the device configuration file")

        power = TargetFactory.create_power_control(
            config.pop_optional(Configuration, 'power'), ssh or serial)

        config.ensure_consumed()

        board = Board('Test board', console=consoles, power=power,
                      system=system)
        return PlumaContext(board, variables=variables)

    @staticmethod
    def print_context_settings(context: PlumaContext):
        log.log('Components:', bold=True)

        serial = context.board.get_console('serial')
        suffix = 'Default' if serial and context.board.console is serial else None
        TargetConfig.print_component('Serial', serial, suffix)

        ssh = context.board.get_console('ssh')
        suffix = 'Default' if ssh and context.board.console is ssh else None
        TargetConfig.print_component('SSH', ssh, suffix)

        TargetConfig.print_component('Prompt', context.board.system.prompt_regex)
        TargetConfig.print_component('Login', context.board.system.credentials.login)
        TargetConfig.print_component(
            'Password', '******' if context.board.system.credentials.password else None)
        TargetConfig.print_component('Power control', context.board.power)
        TargetConfig.print_component('Storage', context.board.storage)
        TargetConfig.print_component('USB Hub', context.board.hub)
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
    def parse_variables(variables_config: Optional[Configuration]) -> dict:
        if not variables_config:
            return {}

        return variables_config.content()

    @staticmethod
    def parse_credentials(credentials_config: Optional[Configuration]) -> Credentials:
        if not credentials_config:
            return Credentials()

        credentials = Credentials(
            credentials_config.pop(str, 'login', context='credentials'),
            credentials_config.pop_optional(str, 'password', context='credentials'))
        credentials_config.ensure_consumed()
        return credentials

    @staticmethod
    def parse_system_context(system_config: Optional[Configuration]) -> SystemContext:
        if not system_config:
            return SystemContext()

        credentials = TargetFactory.parse_credentials(
            system_config.pop_optional(Configuration, 'credentials'))
        prompt_regex = system_config.pop_optional(str, 'prompt_regex', context='system')
        system = SystemContext(prompt_regex=prompt_regex, credentials=credentials)
        system_config.ensure_consumed()
        return system

    @staticmethod
    def create_consoles(config: Optional[Configuration],
                        system: SystemContext) -> Dict[str, ConsoleBase]:
        if not config:
            return {}

        consoles = {}
        serial = TargetFactory.create_serial(
            config.pop_optional(Configuration, 'serial'), system)
        if serial:
            consoles['serial'] = serial

        ssh = TargetFactory.create_ssh(
            config.pop_optional(Configuration, 'ssh'), system)
        if ssh:
            consoles['ssh'] = ssh

        while(config):
            console_name, console_dict = config.popitem()
            console_config = Configuration(console_dict)
            console_type = console_config.pop(str, 'type')
            if console_type == 'ssh':
                console = TargetFactory.create_ssh(console_config, system)
            elif console_type == 'serial':
                console = TargetFactory.create_serial(console_config, system)
            else:
                raise TargetConfigError(f'Unknown console type {console_type}. '
                                        'Console type must be "ssh" or "serial"')
            consoles[console_name] = console

        config.ensure_consumed()
        return consoles

    @staticmethod
    def create_serial(serial_config: Optional[Configuration],
                      system: Optional[SystemContext]) -> Optional[ConsoleBase]:
        if not serial_config:
            return None

        log.debug(f'Serial config = {serial_config}')

        port = serial_config.pop(str, 'port', context='serial console')
        baudrate = serial_config.pop_optional(int,
                                              'baudrate', default=115200, context='serial console')
        logfile = serial_config.pop_optional(str, 'log_file', context='serial console')
        serial = SerialConsole(port=port, system=system,
                               baud=baudrate, raw_logfile=logfile)
        serial_config.ensure_consumed()
        return serial

    @staticmethod
    def create_ssh(ssh_config: Optional[Configuration],
                   system: SystemContext) -> Optional[ConsoleBase]:
        if not ssh_config:
            return None

        log.debug('SSH config = ' + json.dumps(ssh_config.content()))
        target = ssh_config.pop(str, 'target', context='ssh')
        login = ssh_config.pop_optional(str, 'login', system.credentials.login,
                                        context='ssh')
        password = ssh_config.pop_optional(str, 'password', system.credentials.password,
                                           context='ssh')
        log_file = ssh_config.pop_optional(str, 'log_file', context='ssh')
        ssh_config.ensure_consumed()

        # Create a new system config to override default credentials
        ssh_system = deepcopy(system)
        ssh_system.credentials.login = login
        ssh_system.credentials.password = password

        return SSHConsole(target, system=ssh_system, raw_logfile=log_file)

    @staticmethod
    def create_power_control(power_config: Optional[Configuration],
                             console: Optional[ConsoleBase]) -> Optional[PowerBase]:
        if not power_config:
            power_config = Configuration()

        POWER_SOFT = 'soft'
        POWER_IPPOWER9258 = 'ippower9258'
        POWER_UHUBCTL = 'uhubctl'
        POWER_LIST = [POWER_SOFT, POWER_IPPOWER9258, POWER_UHUBCTL]

        if len(power_config) > 1:
            raise TargetConfigError(
                'Only one power control should be provided in the target configuration,'
                f' but two or more provided:{os.linesep}{power_config}')

        if power_config:
            control_type = power_config.first()
        elif console:
            control_type = POWER_SOFT
        else:
            return None

        if control_type not in POWER_LIST:
            raise TargetConfigError(
                f'Unsupported power control type "{control_type}". '
                f'Supported types: {POWER_LIST}')

        power_config = power_config.pop_optional(Configuration,
                                                 control_type, default=Configuration(),
                                                 context='power control')
        reboot_delay = power_config.pop_optional(int,
                                                 'reboot_delay', context='power control')
        power: PowerBase
        if control_type == POWER_SOFT:
            if not console:
                raise TargetConfigError(
                    'No console available for soft power control')

            on_cmd = power_config.pop_optional(str, 'on_cmd', context='Soft power')
            off_cmd = power_config.pop_optional(str, 'off_cmd', context='Soft power')
            power = SoftPower(console, on_cmd=on_cmd, off_cmd=off_cmd,
                              reboot_delay=reboot_delay)

        elif control_type == POWER_IPPOWER9258:
            host = power_config.pop(str, 'host', context='IP Power PDU')
            outlet = power_config.pop(int, 'outlet', context='IP Power PDU')
            port = power_config.pop_optional(int, 'port', context='IP Power PDU')
            login = power_config.pop_optional(str, 'login', context='IP Power PDU')
            password = power_config.pop_optional(str, 'password', context='IP Power PDU')
            power = IPPowerPDU(port=outlet, host=host, netport=port,
                               username=login, password=password,
                               reboot_delay=reboot_delay)
        elif control_type == POWER_UHUBCTL:
            power = Uhubctl(location=power_config.pop(str, 'location', context='UHubCtl'),
                            port=power_config.pop(int, 'port', context='UHubCtl'),
                            reboot_delay=reboot_delay)
        else:
            raise Exception('Unreachable, unknown power controller')

        power_config.ensure_consumed()
        return power
