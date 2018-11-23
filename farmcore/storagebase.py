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
    def mount_host(self):
        print("--- Manual Intervention Required! ---")
        input("Mount host storage at /tmp/boardmount, then press <ENTER>")

    def unmount_host(self):
        print("--- Manual Intervention Required! ---")
        input("Unmount /tmp/boardmount, then press <ENTER>")

    def mount_board(self):
        print("--- Manual Intervention Required! ---")
        input("Mount board storage at /tmp/boardmount, then press <ENTER>")

    def unmount_board(self):
        print("--- Manual Intervention Required! ---")
        input("Unmount /tmp/boardmount, then press <ENTER>")