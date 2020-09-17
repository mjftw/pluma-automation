import os
import string
import random

from .test import TestBase, TaskFailed
from .shelltest import CommandRunner
from pluma import HostConsole


class ExecutableTest(TestBase):
    '''Takes an executable, deploys and runs it during the test.

    By default, this test will try to deploy the executable on the target
    and run it. This can be changed to run an executable on the host, or on
    the target directly, skipping the deployment.
    '''

    def __init__(self, board, executable_file, host_file=True, run_on_host=False, timeout=None):
        super().__init__(self)
        self.board = board
        self.executable_file = executable_file
        self.host_file = host_file
        self.run_on_host = run_on_host
        self.timeout = timeout if timeout is not None else 5

        if self.host_file and not os.path.isfile(executable_file):
            raise ValueError(
                f'File {executable_file} does not exist on host')

        self.executable_file = os.path.abspath(self.executable_file)

        self._test_name += f'[{self.executable_file}]'

        if self.run_on_host:
            if not self.host_file:
                raise ValueError(
                    f'Cannot run an executable for test "{self}" on host that is not present on the host machine')
        else:
            if not self.board.console:
                raise ValueError(
                    f'Cannot run executable test "{self}" on target: no console'
                    ' was defined. Define a console in "pluma-target.yml", or use '
                    ' "run_on_host" test attribute to run on the host instead.')

            if not self.board.console.support_file_copy():
                raise ValueError(
                    f'The console used ({self.board.console}) does not support file copy. Use a different console'
                    ' like SSH, or run the test on the host')

    def test_body(self):
        filepath = ''
        console = None
        temp_folder = None
        if self.run_on_host:
            console = HostConsole('sh')
            filepath = self.executable_file
        else:
            console = self.board.console
            if self.host_file:
                temp_folder = self.random_folder_name()
                CommandRunner.run(test_name=self._test_name, command=f'mkdir {temp_folder}',
                                  console=console, timeout=self.timeout)
                destination = os.path.join(
                    temp_folder, os.path.basename(self.executable_file))
                console.copy_to_target(self.executable_file, destination)
                filepath = destination
            else:
                filepath = self.executable_file

        if not console:
            raise TaskFailed(
                f'Failed to run script test "{self}": no console available')

        try:
            CommandRunner.run(test_name=self, command=filepath,
                              console=console, timeout=self.timeout)
        finally:
            if temp_folder:
                CommandRunner.run(test_name=self, command=f'rm -r {temp_folder}',
                                  console=console, timeout=self.timeout)

    def random_folder_name(self):
        characters = string.ascii_letters + string.digits
        return 'pluma-' + ''.join(random.choice(characters) for i in range(10))
