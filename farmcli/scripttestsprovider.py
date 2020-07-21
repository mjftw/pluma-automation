from farmcore.baseclasses import Logger
from farmtest import ShellTest
from farmcli import Configuration, TestsConfigError
from .config import TestDefinition, TestsProvider

log = Logger()


class ScriptTestsProvider(TestsProvider):
    def __init__(self):
        pass

    def configuration_key(self):
        return 'script_tests'

    def all_tests(self, config):
        log.log('Inline tests (pluma.yml):', bold=True)
        if not config:
            log.log('    None\n')
            return []

        if isinstance(config, Configuration):
            config = config.content()

        selected_tests = []
        for test_name in config:
            log.log(f'    [x] {test_name}', color='green')

            try:
                test_parameters = config[test_name]
                test_parameters['name'] = test_name
                test = TestDefinition(test_name, testclass=ShellTest,
                                      parameter_sets=[test_parameters], selected=True)
                selected_tests.append(test)
            except Exception as e:
                raise TestsConfigError(
                    f'Failed to parse script test "{test_name}":\n    {e}')

        log.log('')
        return selected_tests
