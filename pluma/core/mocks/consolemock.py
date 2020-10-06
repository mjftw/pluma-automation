from ..baseclasses import ConsoleBase


class ConsoleMock(ConsoleBase):
    def __init__(self):
        super().__init__(self)
        self.engine.open(console_cmd='bash')

    def is_open(self):
        self.log('Mock method called: is_open()')

    def open(self):
        self.log('Mock method called: open()')

    def close(self):
        self.log('Mock method called: close()')
