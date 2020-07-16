import os
import re

from .test import TestBase, TaskFailed
from farmcore import HostConsole


class ShellTest(TestBase):
    shell_test_index = 0

    def __init__(self, board, script, name=None, should_print=None, should_not_print=None, run_on_host=False, timeout=None):
        super().__init__(self)
        self.board = board
        self.should_print = should_print or []
        self.should_not_print = should_not_print or []
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
        received, _ = console.send(
            script, receive=True, timeout=self.timeout or -1, log_verbose=False)
        if received.startswith(script):
            received = received[len(script):]
        received = received.strip()

        prefix = f'Script test "{self.name}":'
        if not received:
            raise TaskFailed(f'{prefix} No response available')

        formatted_received = ''
        first_line = True
        for line in received.splitlines():
            if not first_line:
                formatted_received += '            '
            formatted_received += f'{line}\n'
            first_line = False

        sent_line = f'  Sent:     $ {script}\n'
        should_print_line = f'  Expected: {self.should_print}\n'
        should_not_print_line = f'  Errors:   {self.should_not_print}\n'
        received_line = f'  Received: {formatted_received}'

        if self.output_matches_pattern(self.should_not_print, received):
            raise TaskFailed(
                f'{prefix} Response matched error condition:\n' +
                sent_line + should_not_print_line + received_line)

        if len(self.should_print) > 0:
            response_valid = self.output_matches_pattern(
                self.should_print, received)

            if not response_valid:
                raise TaskFailed(
                    f'{prefix} Response did not match expected:\n' +
                    sent_line + should_print_line + received_line)
            else:
                self.board.log(
                    f'{prefix} Matching response found:\n' +
                    sent_line + should_print_line + received_line)
        else:
            self.board.log(
                f'{prefix}\n' + sent_line + received_line)

        retcode_received, matched = console.send(
            'echo retcode=$?', match='retcode=0', log_verbose=False)
        if matched == False:
            raise TaskFailed(
                f'{prefix} Command "{script}" returned with a non-zero exit code\n' + sent_line + received_line + '  Return code: {retcode_received}')

        # Be sure nothing stays in the buffer
        console.wait_for_quiet(verbose=False)

    def output_matches_pattern(self, patterns, output):
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
