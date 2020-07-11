import json
import logging

from farmcore import Board
from farmcore import SerialConsole, SoftPower

log = logging.getLogger(__name__)


class TargetConfig:
    @staticmethod
    def create_board(config):
        serial = TargetFactory.create_serial(config)
        power = TargetFactory.create_power_control(config, serial)

        print('Components:')
        print(f'    Serial: {str(serial)}')
        print(f'    Power: {str(power)}')

        board = Board('Test board', console=serial, power=power)
        return board


class TargetFactory:
    @ staticmethod
    def create_serial(serial_config):
        if not serial_config:
            return None

        log.debug('Serial config = ' + json.dumps(serial_config))

        port = serial_config.get('port')
        if not port:
            return None

        return SerialConsole(port, int(serial_config.get('baud') or 115200))

    @ staticmethod
    def create_power_control(power_config, serial):
        if serial:
            return SoftPower(serial)
        else:
            return None
