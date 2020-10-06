import os
import re
from typing import List

from pluma.core.baseclasses import ConsoleBase, Logger
from pluma.test import TestingException, TaskFailed

log = Logger()


class CommandRunner():
    @staticmethod
    def run(test_name: str, console: ConsoleBase, command: str, timeout: int = None) -> str:
        '''Run a command in a Shell context'''
        retcode_token = 'pluma-retcode='
        base_command = command
        command += f' ; echo {retcode_token}$?'
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
            raise TestingException('Failed to find return code value')

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
        log.log(CommandRunner.format_command_log(sent=base_command, output=output))

        return output

    @staticmethod
    def run_raw(test_name: str, console: ConsoleBase, command: str, timeout: int = None) -> str:
        '''Run a command with minimal assumptions regarding the context'''
        output = console.send_and_read(command, timeout=timeout, quiet_time=timeout)
        output = CommandRunner.cleanup_command_output(command, output)

        if not output:
            CommandRunner.log_error(test_name=test_name, sent=command, output=output,
                                    error='No response received after sending command')
        else:
            message = CommandRunner.format_command_log(sent=command, output=output)
            log.log(message)

        return output

    @staticmethod
    def log_error(test_name: str, sent: str, output: str, error: str,
                  match_regex: List[str] = None, error_regex: List[str] = None):
        message = f'Script test "{test_name}": {error}:{os.linesep}'
        message += CommandRunner.format_command_log(sent=sent, output=output,
                                                    match_regex=match_regex,
                                                    error_regex=error_regex)
        raise TaskFailed(message)

    @staticmethod
    def format_command_log(sent: str, output: str, match_regex=None, error_regex=None):
        '''Return a formatted log output regarding a command and its output'''
        formatted_output = ''
        first_line = True
        for line in output.splitlines():
            if not first_line:
                formatted_output += '            '
            formatted_output += f'{line}{os.linesep}'
            first_line = False

        sent_line = f'  Sent:     $ {sent}{os.linesep}'
        match_regex_line = f'  Expected: {match_regex}{os.linesep}' if match_regex else ''
        error_regex_line = f'  Errors:   {error_regex}{os.linesep}' if error_regex else ''
        output_line = f'  Output:   {formatted_output}'

        message = sent_line
        message += match_regex_line
        message += error_regex_line
        message += output_line
        return message

    @staticmethod
    def check_output(test_name: str, command: str, output: str,
                     match_regex: List[str], error_regex: List[str]):
        '''Check that command output includes expected content, and no error content'''
        if CommandRunner.output_matches_any_pattern(error_regex, output):
            CommandRunner.log_error(test_name=test_name, sent=command, output=output,
                                    error_regex=error_regex,
                                    error='Response matched an error pattern')

        if not CommandRunner.output_matches_all_patterns(match_regex, output):
            CommandRunner.log_error(test_name=test_name, sent=command, output=output,
                                    match_regex=match_regex,
                                    error='Response did not match all expected patterns')

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
    def output_matches_all_patterns(patterns: List[str], output: str) -> bool:
        '''Return whether the output matches all patterns or not.'''
        if not patterns:
            return True

        if not isinstance(patterns, list):
            patterns = [patterns]

        for pattern in patterns:
            if not re.search(pattern, output, re.MULTILINE):
                return False

        return True

    @staticmethod
    def output_matches_any_pattern(patterns: List[str], output: str) -> bool:
        '''Return whether the output matches any of the pattern or not.'''
        if not patterns:
            return False

        if not isinstance(patterns, list):
            patterns = [patterns]

        for pattern in patterns:
            if re.search(pattern, output, re.MULTILINE):
                return True

        return False
