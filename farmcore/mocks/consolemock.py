import pexpect

from ..baseclasses import ConsoleBase


class ConsoleMock(ConsoleBase):
    def __init__(self):
        # _pex is transport later specific
        self._pex = pexpect.spawn('bash')

        ConsoleBase.__init__(self)

    def is_open(self):
        self.log('Mock method called: is_open()')

    @ConsoleBase.open
    def open(self):
        self.log('Mock method called: open()')

    @ConsoleBase.close
    def close(self):
        self.log('Mock method called: close()')
