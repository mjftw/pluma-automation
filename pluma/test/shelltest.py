from pluma.core.baseclasses import Logger
from pluma import HostConsole, Board
from pluma.test import CommandRunner, TestBase, TaskFailed

log = Logger()


class ShellTest(TestBase):
    shell_test_index = 0

    def __init__(self, board: Board, script: str, name: str = None,
                 should_match_regex: list = None,  should_not_match_regex: list = None,
                 run_on_host: bool = False, timeout: int = None,  runs_in_shell: bool = True,
                 login_automatically: bool = True):
        super().__init__(board)
        self.run_on_host = run_on_host
        self.timeout = timeout if timeout is not None else 5
        self.runs_in_shell = runs_in_shell
        self.login_automatically = login_automatically

        self.scripts = script
        if not isinstance(self.scripts, list):
            self.scripts = [self.scripts]

        if name:
            self._test_name += f'[{name}]'
        else:
            ShellTest.shell_test_index += 1
            self._test_name += f'[{ShellTest.shell_test_index}]'

        if not self.run_on_host and not self.board.console:
            raise ValueError(
                f'Cannot run script test "{self._test_name}" on target: no console'
                ' was defined. Define a console in "pluma-target.yml", or use '
                ' "run_on_host" test attribute to run on the host instead.')

    def test_body(self):
        console = None
        if self.run_on_host:
            console = HostConsole('sh')
        else:
            console = self.board.console
            if not console:
                raise TaskFailed(
                    f'Failed to run script test "{self._test_name}": no console available')

            if self.runs_in_shell and self.login_automatically and console.requires_login:
                self.board.login()

        for script in self.scripts:
            self.run_command(console, script)

    def run_command(self, console, script):
        if self.runs_in_shell:
            output = CommandRunner.run(test_name=self._test_name, console=console,
                                       command=script, timeout=self.timeout)
        else:
            output = CommandRunner.run_raw(test_name=self._test_name, console=console,
                                           command=script, timeout=self.timeout)

        if self.should_match_regex or self.should_not_match_regex:
            CommandRunner.check_output(test_name=self._test_name, command=script, output=output,
                                       match_regex=self.should_match_regex,
                                       error_regex=self.should_not_match_regex)
