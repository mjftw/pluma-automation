from farmclass import Farmclass


class Interact(Farmclass):
    """ Mixes a Console and Shell (Dynamic inheritance)"""
    def __init__(self, console=None, shell=None):
        self.console = console
        self.shell = shell

    def __getattr__(self, attr):
        """ If this class does not have an attribute,
        check if shell or console have it """
        if self.shell and hasattr(self.shell, attr):
            return getattr(self.shell, attr)
        if self.console and hasattr(self.console, attr):
            return getattr(self.console, attr)
        else:
            raise AttributeError("Neither {}, shell, or console have attribute".format(__name__))

    def switch_console(self, console):
        if self.console and self.console.is_open:
            self.console.close()
        self.console = console
        if self.shell:
            self.shell.console = self.console

    def switch_shell(self, shell):
        self.shell = shell
