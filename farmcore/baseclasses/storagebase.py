import re
import os
import time
import tempfile

from .farmclass import Farmclass
from farmutils import run_host_cmd


class StorageError(Exception):
    pass


class StorageBase(Farmclass):
    '''
    Base class for storage classes that can be switched between
    the host and board.
    '''

    host_mountpoint = None
    def __init__(self):
        if type(self) is StorageBase:
            raise AttributeError(
                'This is a base class, and must be inherited')

    def __bool__(self):
        ''' Base class is falsey. Must inherit'''
        return True if type(self) is not StorageBase else False

    def to_host(self):
        ''' Switch storage to the host '''
        raise NotImplemented('This method must be implimented by inheriting class')

    def to_board(self):
        ''' Switch storage to the board '''
        raise NotImplemented('This method must be implimented by inheriting class')

    def mount_host(self, devnode, mountpoint=None, max_tries=5):
        mountpoint = mountpoint or self.host_mountpoint
        if not mountpoint:
            self.host_mountpoint = tempfile.mkdtemp(suffix='_lab')
            mountpoint = self.host_mountpoint

        success = False
        for _ in range(0, max_tries):
            # Check if already mounted
            (output, ret) = run_host_cmd('mount')

            # Unmount if mounted
            if re.search('{}.*'.format(devnode), output):
                self.unmount_host(devnode)

            if not os.path.isdir(mountpoint):
                os.mkdir(mountpoint)

            (output, ret) = run_host_cmd('mount {} {}'.format(devnode, mountpoint))
            if ret == 0:
                success = True
                break

            time.sleep(1)

        if not success:
            raise StorageError('Failed to mount {} at {} after {} attemps: [ERR-{}] {}'.format(
                devnode, mountpoint, max_tries, ret, output))

    def unmount_host(self, devnode, max_tries=5):
        # Check if actually mounted, and unmount until not mounted

        errno = None
        errmsg = None
        max_umounts_per_try = 10

        success = False
        for _ in range(0, max_tries):
            if success:
                break
            for _ in range(0, max_umounts_per_try):
                if self.devnode_is_mounted(devnode):
                    (output, ret) = run_host_cmd('umount {}'.format(devnode))
                    if ret == 0:
                        if not self.devnode_is_mounted(devnode):
                            success = True
                            break
                    else:
                        errno = ret
                        errmsg = output
                else:
                    success = True
                    break

            time.sleep(1)

        if not success:
            raise StorageError(
                'Unmount failed after {} attempts[ERR-{}] {}'.format(
                    max_tries, errno, errmsg))

    def devnode_is_mounted(self, devnode):
        (output, ret) = run_host_cmd('mount')
        if re.search('{}.*'.format(devnode), output):
            return True
        else:
            return False
    # TODO: Impliment these
    def mount_board(self):
        print("--- Manual Intervention Required! ---")

    def unmount_board(self):
        print("--- Manual Intervention Required! ---")

