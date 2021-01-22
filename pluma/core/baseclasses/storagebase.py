import re
import os
import time
import tempfile
from abc import ABCMeta, abstractmethod

from .hardwarebase import HardwareBase
from pluma.utils import run_host_cmd

# FIXME: This class is unfinished, and does not conform with other base classes.


class StorageError(Exception):
    pass


class StorageBase(HardwareBase, metaclass=ABCMeta):
    '''
    Base class for storage classes that can be switched between
    the host and board.
    '''

    host_mountpoint = None

    @abstractmethod
    def to_host(self):
        ''' Switch storage to the host '''

    @abstractmethod
    def to_board(self):
        ''' Switch storage to the board '''

    def mount_host(self, devnode, mountpoint=None, max_tries=5):
        if max_tries <= 0:
            raise ValueError(f'Invalid tries number "{max_tries}"')

        mountpoint = mountpoint or self.host_mountpoint
        if not mountpoint:
            self.host_mountpoint = tempfile.mkdtemp(suffix='_lab')
            mountpoint = self.host_mountpoint

        success = False
        output = ''
        ret = None
        for _ in range(max_tries):
            # Check if already mounted
            (output, ret) = run_host_cmd('mount')

            # Unmount if mounted
            if re.search(fr'{devnode}.*', output):
                self.unmount_host(devnode)

            if not os.path.isdir(mountpoint):
                os.mkdir(mountpoint)

            (output, ret) = run_host_cmd(f'mount {devnode} {mountpoint}')
            if ret == 0:
                success = True
                break

            time.sleep(1)

        if not success:
            raise StorageError(f'Failed to mount {devnode} at {mountpoint} after '
                               f'{max_tries} attemps: [ERR-{ret}] {output}')

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
