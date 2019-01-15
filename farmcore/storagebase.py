import re
import os

from farmutils.helpers import run_host_cmd


class StorageException(Exception):
    pass


class StorageBase():
    '''
    Base class for storage classes that can be switched between
    the host and board.
    '''

    host_mountpoint = None

    def to_host(self):
        ''' Switch storage to the host '''
        raise NotImplemented('This method must be implimented by inheriting class')

    def to_board(self):
        ''' Switch storage to the board '''
        raise NotImplemented('This method must be implimented by inheriting class')

    def mount_host(self, devnode, mountpoint=None):
        mountpoint = mountpoint or self.host_mountpoint
        if not mountpoint:
            raise StorageException('Mount failed: No mountpoint given')

        # Check if already mounted
        (output, ret) = run_host_cmd('mount')

        # Unmount if mounted
        if re.search('{}.*'.format(devnode), output):
            self.unmount_host(devnode)

        if not os.path.isdir(mountpoint):
            os.mkdir(mountpoint)

        (output, ret) = run_host_cmd('mount {} {}'.format(devnode, mountpoint))
        if ret != 0:
            raise StorageException('Failed to mount {} at {}: [ERR-{}] {}'.format(
                devnode, mountpoint, ret, output))

    def unmount_host(self, devnode):
        # Check if actually mounted, and unmount until not mounted
        (output, ret) = run_host_cmd('mount')
        tries = 0
        max_tries = 10

        while re.search('{}.*'.format(devnode), output) and tries < max_tries:
            (output, ret) = run_host_cmd('umount {}'.format(devnode))
            if ret != 0:
                raise StorageException('Unmount failed [ERR-{}] {}'.format(ret, output))
            tries += 1
            (output, ret) = run_host_cmd('mount')

        if tries >= max_tries:
            raise StorageException('Unmount failed after {} attempts'.format(tries))

    # TODO: Impliment these
    def mount_board(self):
        print("--- Manual Intervention Required! ---")

    def unmount_board(self):
        print("--- Manual Intervention Required! ---")

