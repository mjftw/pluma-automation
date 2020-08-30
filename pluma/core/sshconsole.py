import subprocess

from .hostconsole import HostConsole, ConsoleCannotOpenError
from .baseclasses import SystemContext


class SSHConsole(HostConsole):
    def __init__(self, target: str, system: SystemContext = None):
        self.target = target

        if not target:
            raise ValueError("A host/target must be provided for an SSH console")

        if not system.credentials.login:
            raise ValueError("A login must be provided for an SSH console")

        login = system.credentials.login
        password = system.credentials.password

        if not password:
            command = f'ssh {login}@{target} -o StrictHostKeyChecking=no'
        else:
            command = \
                f'sshpass -p {password} ssh {login}@{target}' \
                ' -o PreferredAuthentications=password' \
                ' -o PubkeyAuthentication=no -o StrictHostKeyChecking=no'

        super().__init__(command, system=system)

    def open(self):
        try:
            super().open()
            self.wait_for_prompt(timeout=5)
        except Exception:
            raise ConsoleCannotOpenError

    def support_file_copy(self):
        return True

    def copy_to_host(self, source, destination, timeout=30):
        return self._scp_copy(f'{self.system.credentials.login}@{self.target}:{source}',
                              destination, timeout=timeout)

    def copy_to_target(self, source, destination, timeout=30):
        return self._scp_copy(source,
                              f'{self.system.credentials.login}@{self.target}:{destination}',
                              timeout=timeout)

    def _scp_copy(self, scp_source, scp_destination, timeout=30):
        command = f'scp {scp_source} {scp_destination}'
        if self.login_pass:
            command = f'sshpass -p {self.login_pass} {command}'

        try:
            command_list = command.split()
            subprocess.check_output(command_list, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise Exception(
                f'Failed to copy (scp) "{scp_source}" to "{scp_destination}".\n'
                f'  Command {command} failed with error:\n'
                f'    "{e.output.decode()}"')
