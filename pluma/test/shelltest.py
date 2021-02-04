from typing import List, Optional, Union

from pluma.core.baseclasses import Logger
from pluma import HostConsole, Board
from pluma.core.baseclasses import ConsoleBase
from pluma.test import CommandRunner, TestBase, TaskFailed

log = Logger()


class ShellTest(TestBase):
    '''Execute script within the target (or host) shell'''

    def __init__(self, board: Board, script: Union[str, List[str]], name: str = None,
                 should_match_regex: List[str] = None,
                 should_not_match_regex: List[str] = None, run_on_host: bool = False,
                 timeout: Optional[float] = None,  runs_in_shell: bool = True,
                 login_automatically: bool = False):
        super().__init__(board, test_name=name)
        self.should_match_regex = should_match_regex
        self.should_not_match_regex = should_not_match_regex
        self.run_on_host = run_on_host
        self.timeout = timeout if timeout is not None else 5.0
        self.runs_in_shell = runs_in_shell
        self.login_automatically = login_automatically

        if isinstance(script, str):
            self.scripts = [script]
        else:
            self.scripts = script

        if not self.run_on_host and not self.board.console:
            raise ValueError(
                f'Cannot run script test "{self._test_name}" on target: no console'
                ' was defined. Define a console in "pluma-target.yml", or use '
                ' "run_on_host" test attribute to run on the host instead.')

    def test_body(self):
        self.run_commands()

    def run_commands(self, console: Optional[ConsoleBase] = None,
                     scripts: List[str] = None,
                     timeout: Optional[int] = None) -> str:
        scripts = scripts or self.scripts

        if console is None:
            if self.run_on_host:
                console = HostConsole('sh')
            else:
                console = self.board.console
                if not console:
                    raise TaskFailed(f'Failed to run script test "{self._test_name}": '
                                     'no console available')

        if self.runs_in_shell and self.login_automatically and console.requires_login:
            self.board.login()

        output = ''
        for script in scripts:
            output += self.run_command(console=console, script=script, timeout=timeout)

        return output

    def run_command(self, console: ConsoleBase, script: str,
                    timeout: Optional[float] = None) -> str:
        timeout = timeout or self.timeout

        if self.runs_in_shell:
            output = CommandRunner.run(test_name=self._test_name, console=console,
                                       command=script, timeout=timeout)
        else:
            output = CommandRunner.run_raw(test_name=self._test_name, console=console,
                                           command=script, timeout=timeout)

        if self.should_match_regex or self.should_not_match_regex:
            CommandRunner.check_output(test_name=self._test_name, command=script, output=output,
                                       match_regex=self.should_match_regex,
                                       error_regex=self.should_not_match_regex)

        log.log(CommandRunner.format_command_log(sent=script, output=output))
        return output
