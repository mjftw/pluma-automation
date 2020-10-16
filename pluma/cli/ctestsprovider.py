from pluma.core.baseclasses import Logger
from pluma.test import ExecutableTest
from pluma.cli import TestsConfigError
from .config import TestDefinition, TestsProvider
from .testsbuilder import TestsBuilder

log = Logger()


class CTestsProvider(TestsProvider):
    def __init__(self):
        pass

    def display_name(self):
        return 'C tests'

    def configuration_key(self):
        return 'c_tests'

    def all_tests(self, key: str, config):
        if not config:
            return []

        toolchain_file = config.pop('yocto_sdk')
        env_file = config.pop('source_environment')
        if not toolchain_file and not env_file:
            raise TestsConfigError(
                'Missing \'yocto_sdk\' or \'source_environment\' attributes for C tests')

        install_dir = None
        if toolchain_file:
            install_dir = TestsBuilder.install_yocto_sdk(toolchain_file)

        if not env_file:
            env_file = TestsBuilder.get_yocto_sdk_env_file(install_dir)

        all_tests = []
        tests_config = config.pop('tests', default={}).content()
        for test_name in tests_config:
            try:
                test_parameters = tests_config[test_name]
                test_executable = TestsBuilder.build_c_test(
                    target_name=test_name, env_file=env_file,
                    sources=test_parameters.pop('sources'),
                    flags=test_parameters.pop('flags', None))

                test_parameters['executable_file'] = test_executable

                test = TestDefinition(test_name, testclass=ExecutableTest, test_provider=self,
                                      parameter_sets=[test_parameters], selected=True)
                all_tests.append(test)
            except KeyError as e:
                raise TestsConfigError(
                    f'Error processing C test "{test_name}": Missing mandatory attribute {e}')
            except Exception as e:
                raise TestsConfigError(
                    f'Error processing C test "{test_name}": {e}')

        return all_tests
