from pluma.test import ShellTest


class Hello(ShellTest):
    def __init__(self, board, name: str):
        super().__init__(board=board, script=f'echo "Hello {name}!"',
                         run_on_host=True, runs_in_shell=True)
