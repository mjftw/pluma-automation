from .hostconsole import HostConsole

import subprocess


class SSHConsole(HostConsole):
    def __init__(self, target, login, password=None):
        self.target = target
        self.login_user = login
        self.login_pass = password

        command = ''
        if not password:
            command = f'ssh {login}@{target} -o StrictHostKeyChecking=no'
        else:
            command = f'sshpass -p {password} ssh {login}@{target} -o PreferredAuthentications=password -o PubkeyAuthentication=no -o StrictHostKeyChecking=no'

        super().__init__(command)

    def support_file_copy(self):
        return True

    def copy_to_host(self, source, destination, timeout=30):
        return self._scp_copy(f'{self.login_user}@{self.target}:{source}', destination, timeout=timeout)

    def copy_to_target(self, source, destination, timeout=30):
        return self._scp_copy(source, f'{self.login_user}@{self.target}:{destination}', timeout=timeout)

    def _scp_copy(self, source, destination, timeout=30):
        command = f'scp {source} {destination}'
        if self.login_pass:
            command = f'sshpass -p {self.login_pass} {command}'

        try:
            command_list = command.split()
            subprocess.check_output(command_list, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise Exception(
                f'Failed to copy (scp) "{source}" to "{destination}".\n  Command {command} failed with error:\n    "{e.output.decode()}"')
