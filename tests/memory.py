import subprocess
import sys

from farmtest import TestBase, TaskFailed, TestingException


class MemoryFree(TestBase):
    def __init__(self, board, minimum):
        super().__init__(self)
        self.board = board
        self.min_free_memory = minimum

    def test_body(self):
        result = subprocess.run(['cat', '/proc/meminfo'], capture_output=True)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                string = line.decode('ascii')
                if string.startswith('MemFree:'):
                    free_memory_kb = int(string.split()[1])
                    if free_memory_kb < self.min_free_memory:
                        raise TaskFailed(
                            f'The system has less than {self.min_free_memory} KB or RAM available ({free_memory_kb} KB)')
                    else:
                        return

        raise TestingException(
            'Unexpected error running or parsing "cat proc/meminfo"')


class MemoryReadWrite(TestBase):
    def __init__(self, board, size):
        super().__init__(self)
        self.board = board
        self.size = size

    def __repr__(self):
        return f'{self.__module__}[{self.size}]'

    def test_body(self):
        data = [None for _ in range(self.size)]
        for i in range(self.size):
            data[i] = i

        for i in range(self.size):
            if data[i] != i:
                raise Exception('Inconsistency reading from memory')
