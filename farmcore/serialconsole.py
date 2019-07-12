from serial import Serial
from nanocom import Nanocom

import pexpect.fdpexpect

from .baseclasses import ConsoleBase


class SerialConsole(ConsoleBase):
    def __init__(self, port, baud, raw_logfile=None):
        self.port = port
        self.baud = baud
        self.raw_logfile = raw_logfile
        self._timeout = 0.001
        self._serial_logfile_fd = None
        self._ser = None
        self._pex = None
        super().__init__()

    def __repr__(self):
        return "SerialConsole[{}]".format(self.port)

    @property
    def is_open(self):
        if not self._ser or not self._pex:
            return False
        else:
            return self._ser.isOpen()

    @ConsoleBase.open
    def open(self):
        self.log("Trying to open serial port {}".format(self.port))
        self._ser = Serial(
            port=self.port,
            baudrate=self.baud,
            timeout=self._timeout
        )

        self._pex = pexpect.fdpexpect.fdspawn(
            fd=self._ser.fileno(), timeout=self._timeout)

        if not self.is_open:
            raise RuntimeError(
                "Failed to open serial port {} and init pexpect".format(self.port))

        self.log("Init serial {} success".format(self.port))
        return

    @ConsoleBase.close
    def close(self):
        if self.is_open:
            self._ser.flush()
            self._ser.close()
            self._ser = None
            self.log("Closed serial")
        else:
            self.log("Cannot close serial as it is not open")

    def interact(self, exit_char=None):
        if not self.is_open:
            self.open()

        exit_char = exit_char or '¬'

        self.log('Starting interactive console\nPress {} to exit'.format(
            exit_char))

        com = Nanocom(self._ser, exit_character=exit_char)

        com.start()
        try:
            com.join()
        except KeyboardInterrupt:
            pass
        finally:
            self.log('Exiting interactive console...')
            com.close()

