import os
import string
import random

from pluma.test import TestBase, CommandRunner
from pluma.core.baseclasses import ConsoleBase
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
                    f'Cannot run an executable for test "{self}" on host that '
                    'is not present on the host machine')
        else:
            self.check_console_supports_copy(self.board.console)

    def check_console_supports_copy(self, console: ConsoleBase):
        if not console:
            raise ValueError(
                f'Cannot run executable test "{self}" on target: no console'
                ' was defined or set. Define a console in "pluma-target.yml", or use '
                ' "run_on_host" test attribute to run on the host instead.')

        if not console.support_file_copy:
            raise ValueError(
                f'The console used ({console}) does not support file copy. '
                'Use a different console like SSH, or run the test on the host')

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
                self.check_console_supports_copy(console)
                filepath, temp_folder = self.deploy_executable_in_tmp_folder(
                    executable_file=self.executable_file,
                    console=console)
            else:
                filepath = self.executable_file

        try:
            CommandRunner.run(test_name=self, command=filepath,
                              console=console, timeout=self.timeout)
        finally:
            if temp_folder:
                CommandRunner.run(test_name=self, command=f'rm -r {temp_folder}',
                                  console=console, timeout=self.timeout)

    def deploy_executable_in_tmp_folder(self, console: ConsoleBase) -> (str, str):
        '''Deploy the executable, and returns its full path'''
        temp_folder = ExecutableTest.random_folder_name()
        CommandRunner.run(test_name=self._test_name,
                          command=f'mkdir {temp_folder}',
                          console=console, timeout=self.timeout)
        destination = os.path.join(temp_folder,
                                   os.path.basename(self.executable_file))
        console.copy_to_target(source=self.executable_file,
                               destination=destination)

        return destination, temp_folder

    @staticmethod
    def random_folder_name():
        '''Return a random folder name'''
        characters = string.ascii_letters + string.digits
        return 'pluma-' + ''.join(random.choice(characters) for i in range(10))
