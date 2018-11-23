import time
import subprocess

from farmcore import farm
from farmtest.test import TestRunner
from farmtest.unittest import UnitTest, UnitTestSuite
from farmtest import unittestlib


class OverwriteMountsTest():
    def __init__(self, board):
        self.board = board

    def _host_unmount(self):
        subprocess.call(['umount /dev/sdb1'], shell=True)
        time.sleep(1)

    def _host_mount(self):
        self._host_unmount()
        subprocess.call(['mkdir -p /tmp/boardmount'], shell=True)
        subprocess.call(['mount /dev/sdb1 /tmp/boardmount'], shell=True)
        time.sleep(1)

    def _board_mount(self):
        self.board.console.send('mkdir -p /tmp/boardmount')
        self.board.console.send('mount /dev/mmcblk0p1 /tmp/boardmount')
        time.sleep(1)

    def _board_unmount(self):
        self.board.console.send('sync')
        self.board.console.send('umount /dev/mmcblk0p1')
        time.sleep(3)


class ProcessInfoTest():
    def __init__(self, board):
        self.board = board

    def test_body(self):
        self.board.console.send('touch /tmp/boardmount/made_by_lab')
        self.board.console.send('ps aux > /tmp/boardmount/board_test.txt')


class MemStatsTest():
    def __init__(self, board):
        self.board = board

    def test_body(self):
        def unit_vmstat_setup(suite):
            self.board.console.send(
                'vmstat -n 1 > /tmp/boardmount/vmstatdata{} &'.format(
                suite.num_iterations_run))

        def unit_vmstat_body(suite):
            time.sleep(10)

        def unit_vmstat_teardown(suite):
            self.board.console.send('killall vmstat')

        unit_vmstat = UnitTest(
            fsetup=unit_vmstat_setup,
            fbody=unit_vmstat_body,
            fteardown=unit_vmstat_teardown
        )

        UnitTestSuite(
            tests=unit_vmstat,
            run_condition_func=unittestlib.sc_run_n_iterations(3)
        ).run()


def main():
    hub = farm.Hub('1-4.1.3')
    board = farm.Board(
        name='bbb',
        hub=hub,
        bootstr='BeagleBoard',
        power=farm.APC(
            host='10.103.3.41',
            username='apc',
            password='apc',
            port=1
        ),
        storage=farm.SDWire()
    )

    tr = TestRunner(
        board,
        tests=[
            OverwriteMountsTest(board),
            ProcessInfoTest(board),
            MemStatsTest(board)
        ])

    tr.run()

if __name__ == "__main__":
    main()