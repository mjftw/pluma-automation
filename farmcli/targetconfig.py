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
        board = Board('fake', console=serial, power=power)
        return board


class TargetFactory:
    @ staticmethod
    def create_serial(serial_config):
        if not serial_config:
            return None

        log.debug('Serial config = ' + json.dumps(serial_config))

        port = serial_config.get('port') or '/dev/ttyUSB0'
        return SerialConsole(port, serial_config.get('baud'))

    @ staticmethod
    def create_power_control(power_config, serial):
        return SoftPower(serial)
