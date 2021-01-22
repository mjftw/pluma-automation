from pathlib import Path
from typing import List

from pluma.core.baseclasses import Logger
from pluma.core.builder import YoctoCBuilder
from pluma.test import ExecutableTest
from pluma.cli import TestsConfigError
from .config import TestDefinition, TestsProvider, Configuration

log = Logger()


class CTestsProvider(TestsProvider):
    def __init__(self):
        pass

    def display_name(self) -> str:
        return 'C tests'

    def configuration_key(self) -> str:
        return 'c_tests'

    def all_tests(self, key: str, config: Configuration) -> List[TestDefinition]:
        if not config:
            return []

        toolchain_file = config.pop_optional(str, 'yocto_sdk')
        env_file = config.pop_optional(str, 'source_environment')

        if env_file:
            env_file = Path(env_file)
        elif toolchain_file:
            install_dir = YoctoCBuilder.install_yocto_sdk(Path(toolchain_file))
            env_file = YoctoCBuilder.get_yocto_sdk_env_file(install_dir)
        else:
            raise TestsConfigError(
                'Missing "yocto_sdk" or "source_environment" attributes for C tests')

        all_tests = []
        tests_config = config.pop_optional(
            Configuration, 'tests', default=Configuration()).content()
        for test_name in tests_config:
            try:
                test_parameters = tests_config[test_name]
                test_executable = YoctoCBuilder.cross_compile(
                    target_name=test_name, env_file=env_file,
                    sources=test_parameters.pop(list, 'sources', context='c_tests'),
                    flags=test_parameters.pop_optional(list, 'flags', context='c_tests'))

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
