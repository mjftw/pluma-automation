import subprocess
import sys

from farmtest import TestBase, TaskFailed


class MemoryFree(TestBase):
    def __init__(self, board, parameters):
        super().__init__(self)
        self.board = board

        if not isinstance(parameters, dict):
            raise ValueError('Missing parameters for test')

        self.min_free_memory = parameters.get('minimum')
        if not self.min_free_memory:
            raise ValueError('Missing "minimum" test parameter')

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

        raise TaskFailed(
            'Unexpected error running or parsing "cat proc/meminfo"')


class MemoryReadWrite(TestBase):
    def __init__(self, board, parameters):
        super().__init__(self)
        self.board = board

        if not isinstance(parameters, dict):
            raise ValueError('Missing parameters for test')

        self.size = parameters.get('size')
        if not self.size:
            raise ValueError('Missing "size" test parameter')

    def test_body(self):
        [['?'] * 10 for _ in range(self.size)]
