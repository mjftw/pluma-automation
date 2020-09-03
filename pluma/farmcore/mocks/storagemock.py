from ..baseclasses import StorageBase


class StorageMock(StorageBase):
    def __init__(self):
        StorageBase.__init__(self)

    def to_host(self):
        self.log('Mock method called: to_host()')

    def to_board(self):
        self.log('Mock method called: to_board()')

    def mount_host(self, devnode, mountpoint=None, max_tries=None):
        self.log('Mock method called: mount_host()')

    def unmount_host(self, devnode, max_tries=None):
        self.log('Mock method called: unmount_host()')

    def mount_board(self):
        self.log('Mock method called: mount_board()')

    def unmount_board(self):
        self.log('Mock method called: unmount_board()')
