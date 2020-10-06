import pty
import os
import atexit
import sys

from ..baseclasses import ConsoleBase


class SerialConsoleMock(ConsoleBase):
    def __init__(self, child_function=None):
        if child_function:
            assert callable(child_function)

        self.child_function = child_function or self._default_child_function
        self._child_pid = None
        self._child_fd = None

        ConsoleBase.__init__(self)

    @property
    def is_open(self):
        return True if self._child_pid else False

    def open(self):
        if not self.is_open:
            # Spawn child process with a pseudo tty to communicate
            pid, fd = pty.fork()
            if pid != 0:
                # In parent process
                try:
                    atexit.register(self.close)
                except FileExistsError:
                    pass

                self._child_fd = fd
                self._child_pid = pid
                print(f'Spawned child with PID={pid}, and pseudo terminal FD={fd}')
            else:
                # In child process
                self.child_function()
                sys.exit()

            self.engine.open(console_fd=self._child_fd)

    def close(self):
        # Kill child process to close pseudo terminal
        if self.is_open:
            try:
                os.kill(self._child_pid, 0)
            except OSError:
                pass
            os.close(self._child_fd)
            self._child_pid = None
            self._child_fd = None

            try:
                atexit.unregister(self.close)
            except FileExistsError:
                pass

    def _default_child_function(self):
        # echo stdin to stdout
        while True:
            received = input()
            print(received)
