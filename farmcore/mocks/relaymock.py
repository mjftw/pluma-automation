
from ..baseclasses import RelayBase


class RelayMock(RelayBase):
    def __init__(self):
        RelayBase.__init__(self)

    @RelayBase.toggle
    def toggle(self, port, throw):
        self.log('Mock method called: toggle(port={}, throw={})'.format(
            port, throw))
