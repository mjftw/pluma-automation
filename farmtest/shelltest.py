import os

from .test import TestBase, TaskFailed

shell_test_index = 0


class ShellTest(TestBase):
    def __init__(self, board, parameters):
        super().__init__(self)
        self.board = board

        if not isinstance(parameters, dict):
            raise ValueError('Missing parameters for test')

        self.scripts = parameters.get('script')
        if not self.scripts:
            raise ValueError(
                f'Missing "script" attribute in script test: {parameters}')

        if not isinstance(self.scripts, list):
            self.scripts = [self.scripts]

        self.should_print = parameters.get('should_print')
        self.should_not_print = parameters.get('should_not_print')

        global shell_test_index
        shell_test_index = shell_test_index + 1
        self.name = parameters.get(
            'name') or f'{self.__module__}[{shell_test_index}]'

        self.run_on_host = parameters.get('run_on_host') or False
        if not self.run_on_host and not self.board.console:
            raise ValueError(
                f'Cannot run script test "{self.name}" on target: no console'
                ' was defined. Define a console in "pluma-target.yml", or use '
                ' "run_on_host" test attribute to run on the host instead.')

    def __repr__(self):
        return self.name

    def test_body(self):
        if self.run_on_host:
            self.run_host()
        else:
            self.run_target()

    def run_host(self):
        for script in self.scripts:
            ret = os.system(script)
            if ret != 0:
                raise TaskFailed(
                    f'Shell script command "{script}" returned a non-zero code ({ret}).')

    def run_target(self):
        console = self.board.console
        if not console:
            raise TaskFailed(
                f'Failed to run script test "{self.name}": no console available')

        for script in self.scripts:
            console.send(script, match=self.should_print,
                         excepts=self.should_not_print)
