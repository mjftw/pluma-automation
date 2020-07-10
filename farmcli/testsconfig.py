import logging
import yaml

from farmtest import TestController, TestBase, TestRunner

log = logging.getLogger(__name__)


class Config:
    @staticmethod
    def load_configuration(tests_config_path, target_config_path):
        tests_config = None
        target_config = None

        try:
            with open(tests_config_path, 'r') as config:
                tests_config = yaml.load(config, Loader=yaml.FullLoader)
        except FileNotFoundError:
            log.error('Configuration file "' + tests_config_path +
                      '" not found in the current folder')
            exit(-1)
        except:
            log.error('Failed to open configuration file "' +
                      tests_config_path + '"')
            exit(-1)

        try:
            with open(target_config_path, 'r') as config:
                target_config = yaml.load(config, Loader=yaml.FullLoader)
        except FileNotFoundError:
            log.error('Configuration file "' + target_config_path +
                      '" not found in the current folder')
            exit(-1)
        except:
            log.error('Failed to open configuration file "' +
                      target_config_path + '"')
            exit(-1)

        return tests_config, target_config


class TestsConfig:
    @staticmethod
    def create_test_controller(config, board):
        return TestController(
            testrunner=TestRunner(
                board=board,
                tests=TestsConfig.create_test_list(config),
                sequential=config.get('sequential') or True,
                email_on_fail=config.get('email_on_fail') or False,
                continue_on_fail=config.get('continue_on_fail') or True,
                skip_tasks=['_board_on_and_validate',
                            '_board_login', '_board_off'],
            )
        )

    @staticmethod
    def create_test_list(config):
        return [
            EmptyTest()
        ]


class EmptyTest(TestBase):
    def __init__(self):
        super().__init__(self)

    def test_body(self):
        pass
