class StorageBase():
    '''
    Base class for storage classes that can be switched between
    the host and board.
    '''

    def to_host(self):
        ''' Switch storage to the host '''
        raise NotImplemented('This method must be implimented by inheriting class')

    def to_board(self):
        ''' Switch storage to the board '''
        raise NotImplemented('This method must be implimented by inheriting class')

    # TODO: Impliment these
    def mount_host(self, devnode, mountpoint):
        raise NotImplemented

    def unmount_host(self, devnode, mountpoint):
        raise NotImplemented

    def mount_board(self, devnode):
        raise NotImplemented

    def unmount_board(self, devnode, mountpoint):
        raise NotImplemented