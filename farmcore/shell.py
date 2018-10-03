from farmclass import Farmclass


class Shell(Farmclass):
    """ Base class, should be inherited by all Shell Classes """
    def __init__(self, console=None):
        """ A Shell uses a Console object to interact with a board """
        self.console = console
