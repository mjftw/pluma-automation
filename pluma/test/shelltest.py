import os
import re

from pluma.core.baseclasses import ConsoleBase, Logger
from pluma import HostConsole, Board
from .test import TestBase, TaskFailed

log = Logger()


class ShellTest(TestBase):
    shell_test_index = 0

    def __init__(self, board: Board, script: str, name: str = None, should_print: list = None,
                 should_not_print: list = None, run_on_host: bool = False, timeout: int = None,
                 runs_in_shell: bool = True, login_automatically: bool = True):
        super().__init__(board)
        self.should_print = should_print or []
        self.should_not_print = should_not_print or []
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

        if self.should_print or self.should_not_print:
            CommandRunner.check_output(test_name=self._test_name, command=script, output=output,
                                       should_print=self.should_print,
                                       should_not_print=self.should_not_print)


class CommandRunner():
    @staticmethod
    def run(test_name: str, console: ConsoleBase, command: str, timeout: int = None):
        '''Run a command in a Shell context'''
        retcode_token = 'pluma-retcode='
        command += " && echo pluma-retcode=$?"
        output, matched = console.send_and_expect(
            command, timeout=10, match=retcode_token+r'-?\d+')

        if not matched:
            CommandRunner.log_error(test_name=test_name, sent=command, output=output,
                                    error='No response within timeout, or failed device'
                                    ' failed to send return code. If this is not running'
                                    ' in a shell, set "runs_in_shell" to "false".')

        output = re.sub(re.escape(matched) + r'$', '', output)
        retcode_match = re.search(retcode_token+r'(-?\d+)', matched)
        if not retcode_match:
            raise Exception('Failed to find return code value')

        retcode = int(retcode_match.group(1))
        if retcode == 0:
            error = None
        elif retcode is None:
            error = 'failed to retrieve return code for command'
        else:
            error = f'returned with exit code {retcode}'

        if error:
            CommandRunner.log_error(test_name=test_name, sent=command, output=output,
                                    error=f'Command "{command}" {error}')

        output = CommandRunner.cleanup_command_output(command, output)

        if not output:
            CommandRunner.log_error(test_name=test_name, sent=command, output=output,
                                    error='No response received after sending command')
        else:
            message = CommandRunner.format_command_log(sent=command, output=output)
            log.log(message)

        return output

    @staticmethod
    def run_raw(test_name: str, console: ConsoleBase, command: str, timeout: int = None):
        '''Run a command with minimal assumptions regarding the context'''
        output = console.send_and_read(command, timeout=timeout, quiet_time=timeout)
        output = CommandRunner.cleanup_command_output(command, output)

        if not output:
            CommandRunner.log_error(test_name=test_name, sent=command, output=output,
                                    error='No response received after sending command')
        else:
            message = CommandRunner.format_command_log(sent=command, output=output)
            log.log(message)

    @staticmethod
    def log_error(test_name: str, sent: str, output: str, error: str,
                  should_print=None, should_not_print=None):
        message = f'Script test "{test_name}": {error}:{os.linesep}'
        message += CommandRunner.format_command_log(sent=sent, output=output,
                                                    should_print=should_print,
                                                    should_not_print=should_not_print)
        raise TaskFailed(message)

    @staticmethod
    def format_command_log(sent: str, output: str, should_print=None, should_not_print=None):
        '''Return a formatted log output regarding a command and its output'''
        formatted_output = ''
        first_line = True
        for line in output.splitlines():
            if not first_line:
                formatted_output += '            '
            formatted_output += f'{line}{os.linesep}'
            first_line = False

        sent_line = f'  Sent:     $ {sent}{os.linesep}'
        should_print_line = f'  Expected: {should_print}{os.linesep}'
        should_not_print_line = f'  Errors:   {should_not_print}{os.linesep}'
        output_line = f'  Output:   {formatted_output}'

        message = sent_line
        if should_print:
            message += should_print_line
        if should_not_print:
            message += should_not_print_line

        message += output_line
        return message

    @staticmethod
    def check_output(test_name: str, command: str, output: str,
                     should_print: list, should_not_print: list):
        '''Check that command output includes expected content, and no error content'''
        should_print = should_print or []
        should_not_print = should_not_print or []

        if should_not_print:
            if not CommandRunner.output_matches_pattern(should_not_print, output):
                CommandRunner.log_error(test_name=test_name, sent=command, output=output,
                                        should_not_print=should_not_print,
                                        error='Response matched error condition')

        if should_print:
            pattern_matched = CommandRunner.output_matches_pattern(should_print, output)

            if not pattern_matched:
                CommandRunner.log_error(test_name=test_name, sent=command, output=output,
                                        should_print=should_print,
                                        error='Response did not match expected')
            else:
                message = CommandRunner.format_command_log(sent=command, output=output,
                                                           should_print=should_print)
                log.log(message)

    @staticmethod
    def cleanup_command_output(command: str, output: str) -> str:
        '''Return the output of a command only, stripping prompts'''
        command_end = None
        # Look for 2 instances of the command max, as it may echo twice,
        # once as a console echo, and once after the prompt.
        i = 0
        for match in re.finditer(re.escape(command), output):
            i += 1
            if i > 2:
                break

            command_end = match.end(0)

        if command_end:
            output = output[command_end:]

        return output.strip()

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
        '''Return wether the output matches any of the pattern or not.'''
        if patterns is None:
            raise ValueError('None pattern provided')

        if not isinstance(patterns, list):
            patterns = [patterns]

        for pattern in patterns:
            regexp = re.compile(pattern)
            for line in output.splitlines():
                if regexp.search(line):
                    return True

        return False
