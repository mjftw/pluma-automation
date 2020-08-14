import os
import re

from farmcore.baseclasses import ConsoleBase, Logger
from farmcore import HostConsole
from .test import TestBase, TaskFailed


class ShellTest(TestBase):
    shell_test_index = 0

    def __init__(self, board, script, name=None, should_print=None, should_not_print=None, run_on_host=False, timeout=None,  runs_in_shell: bool = True):
        super().__init__(self)
        self.board = board
        self.should_print = should_print or []
        self.should_not_print = should_not_print or []
        self.run_on_host = run_on_host
        self.timeout = timeout if timeout is not None else 5
        self.runs_in_shell = runs_in_shell

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

            self.board.login()

        for script in self.scripts:
            self.run_command(console, script)

    def run_command(self, console, script):
        CommandRunner.run(test_name=self._test_name, console=console, command=script,
                          timeout=self.timeout, should_print=self.should_print, should_not_print=self.should_not_print,
                          runs_in_shell=self.runs_in_shell)


class CommandRunner():
    @staticmethod
    def run(test_name: str, console: ConsoleBase, command: str,
            timeout: int = None, should_print: list = None, should_not_print: list = None, runs_in_shell: bool = True) -> str:
        should_print = should_print or []
        should_not_print = should_not_print or []
        log = Logger()

        output = console.send_and_read(command, timeout=timeout)

        command_end = None
        # Look for 2 instances of the command max, as it may echo twice,
        # once as a console echo, and once after the prompt.
        i = 0
        for match in re.finditer(command, output):
            i += 1
            if i > 2:
                break

            command_end = match.end(0)

        if command_end:
            output = output[command_end:]

        output = output.strip()
        prefix = f'Script test "{test_name}":'
        if not output:
            raise TaskFailed(
                f'{prefix} No response received after sending command')

        formatted_output = ''
        first_line = True
        for line in output.splitlines():
            if not first_line:
                formatted_output += '            '
            formatted_output += f'{line}{os.linesep}'
            first_line = False

        sent_line = f'  Sent:     $ {command}{os.linesep}'
        should_print_line = f'  Expected: {should_print}{os.linesep}'
        should_not_print_line = f'  Errors:   {should_not_print}{os.linesep}'
        output_line = f'  Output:   {formatted_output}'

        if CommandRunner.output_matches_pattern(should_not_print, output):
            raise TaskFailed(
                f'{prefix} Response matched error condition:{os.linesep}' +
                sent_line + should_not_print_line + output_line)

        if should_print:
            response_valid = CommandRunner.output_matches_pattern(
                should_print, output)

            if not response_valid:
                raise TaskFailed(
                    f'{prefix} Response did not match expected:{os.linesep}' +
                    sent_line + should_print_line + output_line)
            else:
                log.log(
                    f'{prefix} Matching response found:{os.linesep}' +
                    sent_line + should_print_line + output_line)
        else:
            log.log(f'{prefix}{os.linesep}' + sent_line + output_line)

        if runs_in_shell:
            retcode = CommandRunner.query_return_code(console)
            if retcode is 0:
                error = None
            elif retcode is None:
                error = 'failed to retrieve return code for command'
            else:
                error = f'returned with exit code {retcode}'

            if error:
                error = f'{prefix} Command "{command}" {error}{os.linesep}' + \
                    sent_line + output_line
                raise TaskFailed(error)

        return output

    @staticmethod
    def query_return_code(console: ConsoleBase):
        '''Query and return the return code of the last command ran.'''
        retcode_output = console.send_and_read('echo retcode=$?')
        if not retcode_output:
            return None

        retcode_match = re.search(r'retcode=(-?\d+)\b', retcode_output,
                                  re.MULTILINE)
        if not retcode_match:
            return None

        return int(retcode_match.group(1))

    @staticmethod
    def output_matches_pattern(patterns, output):
        if patterns is None:
            raise ValueError('None pattern provided')

        if not isinstance(patterns, list):
            patterns = [patterns]

        for pattern in patterns:
            regexp = re.compile(pattern)
            for line in output.splitlines():
                if regexp.match(line) is not None:
                    return True

        return False
