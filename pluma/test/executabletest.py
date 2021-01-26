import os

from pluma.test import TestBase, CommandRunner
from pluma.core.baseclasses import ConsoleBase
from pluma.utils import random_dir_name
from pluma import HostConsole


class ExecutableTest(TestBase):
    '''Takes an executable, deploys and runs it during the test.

    By default, this test will try to deploy the executable on the target
    and run it. This can be changed to run an executable on the host, or on
    the target directly, skipping the deployment.
    '''

    def __init__(self, board, executable_file, host_file=True, run_on_host=False, timeout=None):
        abs_path = os.path.abspath(executable_file)
        super().__init__(test_name=str(abs_path))
        self.board = board
        self.executable_file = abs_path
        self.host_file = host_file
        self.run_on_host = run_on_host
        self.timeout = timeout if timeout is not None else 5

        if self.host_file and not os.path.isfile(abs_path):
            raise ValueError(
                f'File {executable_file} does not exist on host')

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
                f'Cannot run executable test "{self}" on target: no console '
                'was defined or set. Define a console in your target config file, '
                'or use "run_on_host" test attribute to run on the host instead.')

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
                filepath, temp_folder = self.deploy_file_in_tmp_folder(
                    file=self.executable_file, console=console)
            else:
                filepath = self.executable_file

        try:
            CommandRunner.run(test_name=self, command=filepath,
                              console=console, timeout=self.timeout)
        finally:
            if temp_folder:
                CommandRunner.run(test_name=self, command=f'rm -r {temp_folder}',
                                  console=console, timeout=self.timeout)

    def deploy_file_in_tmp_folder(self, file: str, console: ConsoleBase) -> (str, str):
        '''Deploy the file, and returns its full path and containing temporary folder'''
        temp_folder = random_dir_name()
        CommandRunner.run(test_name=self._test_name,
                          command=f'mkdir {temp_folder}',
                          console=console, timeout=self.timeout)
        destination = os.path.join(temp_folder,
                                   os.path.basename(file))
        console.copy_to_target(source=file,
                               destination=destination)

        return destination, temp_folder
