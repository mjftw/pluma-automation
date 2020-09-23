from pluma.test import ShellTest
from pluma import Board


class FileExists(ShellTest):
    def __init__(self, board: Board, path: str):
        super().__init__(board, script=f'[ -e "{path}" ]')


class FileIsRegular(ShellTest):
    def __init__(self, board: Board, path: str):
        super().__init__(board, script=f'[ -f "{path}" ]')


class FileIsDir(ShellTest):
    def __init__(self, board: Board, path: str):
        super().__init__(board, script=f'[ -d "{path}" ]')


class FileIsNotEmpty(ShellTest):
    def __init__(self, board: Board, path: str):
        super().__init__(board, script=f'[ -s "{path}" ]')


class FileIsEmpty(ShellTest):
    def __init__(self, board: Board, path: str):
        super().__init__(board, script=f'[ ! -s "{path}" ]')


class FileIsCharDevice(ShellTest):
    def __init__(self, board: Board, path: str):
        super().__init__(board, script=f'[ -c "{path}" ]')


class FileIsBlockDevice(ShellTest):
    def __init__(self, board: Board, path: str):
        super().__init__(board, script=f'[ -b "{path}" ]')


class FileIsSymlink(ShellTest):
    def __init__(self, board: Board, path: str):
        super().__init__(board, script=f'[ -h "{path}" ]')


class FileIsSocket(ShellTest):
    def __init__(self, board: Board, path: str):
        super().__init__(board, script=f'[ -S "{path}" ]')


class FileIsReadable(ShellTest):
    def __init__(self, board: Board, path: str):
        super().__init__(board, script=f'[ -r "{path}" ]')


class FileIsWritable(ShellTest):
    def __init__(self, board: Board, path: str):
        super().__init__(board, script=f'[ -w "{path}" ]')


class FileIsExecutable(ShellTest):
    def __init__(self, board: Board, path: str):
        super().__init__(board, script=f'[ -x "{path}" ]')

