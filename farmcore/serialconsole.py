from serial import Serial
import sys
import os
import select

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

    def interact(self, echo=False):
        if not self.is_open:
            self.open()

        self.log('Starting interactive console\nPress Ctrl-C to exit')

        try:
            # Disable echo
            os.system("stty -echo")

            self._ser.reset_input_buffer()
            self._ser.reset_output_buffer()
            while True:
                # Send
                # Check if stdin chars are waiting & read until clear
                tx_buf = ''
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    tx_buf += sys.stdin.read(1)
                if tx_buf:
                    tx_str = self.encode(tx_buf)
                    self._pex.write(tx_str)

                # Recieve
                rx_buf = b''
                if self._ser.in_waiting:
                    rx_buf += self._pex.read(self._ser.in_waiting)
                if rx_buf:
                    rx_str = self.decode(rx_buf)
                    sys.stdout.write(rx_str)

        except KeyboardInterrupt:
            self.log('Exiting interactive console')
        finally:
            # Enable echo
            os.system("stty echo")

