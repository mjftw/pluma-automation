from farmclass import Farmclass
from console import Console
from shell import Shell


class Interact(Farmclass):
    """ Mixes a Console and Shell (think dynamic inheritance)"""
    def __init__(self, console=None, shell=None):
        self.console = console
        self.shell = shell

        self.switch_console(self.console)
        self.switch_shell(self.shell)

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
        if console and not isinstance(console, Console):
            raise TypeError("{} is not an instance of Console".format(
                type(console).__name__))

        self.log("Switching console to {}".format(
            type(console).__name__))

        if self.console and self.console.is_open:
            self.console.close()
        self.console = console
        if self.shell:
            self.shell.console = self.console

    def switch_shell(self, shell):
        if shell and not isinstance(shell, Shell):
            raise TypeError("{} is not an instance of Shell".format(
                type(shell).__name__))

        self.log("Switching shell to {}".format(
            type(shell).__name__))

        self.shell = shell
