from pluma.test import ShellTest


class World(ShellTest):
    def __init__(self, board):
        super().__init__(board=board, script='echo "World!"',
                         run_on_host=True, runs_in_shell=True)
