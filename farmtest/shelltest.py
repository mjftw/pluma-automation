import os

from .test import TestBase, TaskFailed
from farmcore import HostConsole


class ShellTest(TestBase):
    shell_test_index = 0

    def __init__(self, board, script, name=None, should_print=[], should_not_print=[], run_on_host=False, timeout=None):
        super().__init__(self)
        self.board = board
        self.should_print = should_print
        self.should_not_print = should_not_print
        self.run_on_host = run_on_host
        self.timeout = timeout

        self.scripts = script
        if not isinstance(self.scripts, list):
            self.scripts = [self.scripts]

        ShellTest.shell_test_index += 1
        self.name = name or f'{self.__module__}[{ShellTest.shell_test_index}]'

        if not self.run_on_host and not self.board.console:
            raise ValueError(
                f'Cannot run script test "{self.name}" on target: no console'
                ' was defined. Define a console in "pluma-target.yml", or use '
                ' "run_on_host" test attribute to run on the host instead.')

    def __repr__(self):
        return self.name

    def test_body(self):
        console = None
        if self.run_on_host:
            console = HostConsole('sh')
        else:
            console = self.board.console
            if not console:
                raise TaskFailed(
                    f'Failed to run script test "{self.name}": no console available')

        for script in self.scripts:
            self.run_command(console, script)

    def run_command(self, console, script):
        received, matched = console.send(script, match=self.should_print,
                                         excepts=self.should_not_print, timeout=self.timeout or -1)

        prefix = f'Script test "{self.name}":'
        if matched == False:
            raise TaskFailed(
                f'{prefix} Response did not match expected:\n'
                f'    Send:     {script}\n'
                f'    Expected: "{self.should_print}"\n'
                f'    Actual: "{received}"')
        elif matched == True:
            print(
                f'{prefix} Matching response found:\n'
                f'    Sent:     "{script}"\n'
                f'    Expected: "{self.should_print}"\n'
                f'    Matching: "{received}"')
        else:
            print(
                f'{prefix} Response received:\n'
                f'    Sent:     "{script}"\n'
                f'    Received: "{received}"')
