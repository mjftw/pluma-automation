from pluma.test import ShellTest
from pluma import Board


class FileExists(ShellTest):
    def __init__(self, board: Board, path: str, run_on_host: bool = False):
        super().__init__(board, script=f'[ -e "{path}" ]', runs_in_shell=True,
                         run_on_host=run_on_host)


class FileIsRegular(ShellTest):
    def __init__(self, board: Board, path: str, run_on_host: bool = False):
        super().__init__(board, script=f'[ -f "{path}" ]', runs_in_shell=True,
                         run_on_host=run_on_host)


class FileIsDir(ShellTest):
    def __init__(self, board: Board, path: str, run_on_host: bool = False):
        super().__init__(board, script=f'[ -d "{path}" ]', runs_in_shell=True,
                         run_on_host=run_on_host)


class FileIsNotEmpty(ShellTest):
    def __init__(self, board: Board, path: str, run_on_host: bool = False):
        super().__init__(board, script=f'[ -s "{path}" ]', runs_in_shell=True,
                         run_on_host=run_on_host)


class FileIsEmpty(ShellTest):
    def __init__(self, board: Board, path: str, run_on_host: bool = False):
        super().__init__(board, script=f'[ ! -s "{path}" ]', runs_in_shell=True,
                         run_on_host=run_on_host)


class FileIsCharDevice(ShellTest):
    def __init__(self, board: Board, path: str, run_on_host: bool = False):
        super().__init__(board, script=f'[ -c "{path}" ]', runs_in_shell=True,
                         run_on_host=run_on_host)


class FileIsBlockDevice(ShellTest):
    def __init__(self, board: Board, path: str, run_on_host: bool = False):
        super().__init__(board, script=f'[ -b "{path}" ]', runs_in_shell=True,
                         run_on_host=run_on_host)


class FileIsSymlink(ShellTest):
    def __init__(self, board: Board, path: str, run_on_host: bool = False):
        super().__init__(board, script=f'[ -h "{path}" ]', runs_in_shell=True,
                         run_on_host=run_on_host)


class FileIsSocket(ShellTest):
    def __init__(self, board: Board, path: str, run_on_host: bool = False):
        super().__init__(board, script=f'[ -S "{path}" ]', runs_in_shell=True,
                         run_on_host=run_on_host)


class FileIsReadable(ShellTest):
    def __init__(self, board: Board, path: str, run_on_host: bool = False):
        super().__init__(board, script=f'[ -r "{path}" ]', runs_in_shell=True,
                         run_on_host=run_on_host)


class FileIsWritable(ShellTest):
    def __init__(self, board: Board, path: str, run_on_host: bool = False):
        super().__init__(board, script=f'[ -w "{path}" ]', runs_in_shell=True,
                         run_on_host=run_on_host)


class FileIsExecutable(ShellTest):
    def __init__(self, board: Board, path: str, run_on_host: bool = False):
        super().__init__(board, script=f'[ -x "{path}" ]', runs_in_shell=True,
                         run_on_host=run_on_host)


class CheckFileSize(ShellTest):
    def __init__(self, board: Board, path: str, min: str = None, max: str = None,
                 run_on_host: bool = False):
        conditions = []
        if min:
            conditions.append(f'[ $(stat --format=%s "{path}") -ge {min} ]')
        if max:
            conditions.append(f'[ $(stat --format=%s "{path}") -le {max} ]')

        script = ' && '.join(conditions)

        super().__init__(board, script=script, runs_in_shell=True, run_on_host=run_on_host)