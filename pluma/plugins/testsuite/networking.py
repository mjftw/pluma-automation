from pluma.test import ShellTest
from pluma import Board


class RespondsToPing(ShellTest):
    def __init__(self, board: Board, target: str = None):
        super().__init__(board, script='')

        if not target:
            ssh_console = board.get_console('ssh')
            if not ssh_console:
                raise ValueError(f'{self}: You need to provide a "target" parameter, '
                                 'or an SSH console to get the target host from.')
            target = ssh_console.target

        self.scripts = [f'ping -c 1 {target}']
        self.run_on_host = True
