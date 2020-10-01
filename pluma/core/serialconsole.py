from serial import Serial
from nanocom import Nanocom

from .baseclasses import ConsoleBase, LogLevel
from .dataclasses import SystemContext


class SerialConsole(ConsoleBase):
    def __init__(self, port, baud, encoding=None, linesep=None,
                 raw_logfile=None, system: SystemContext = None):
        self.port = port
        self.baud = baud
        self._timeout = 0.001
        self._ser = None
        super().__init__(encoding=encoding, linesep=linesep,
                         raw_logfile=raw_logfile, system=system)

    def __repr__(self):
        return "SerialConsole[{}]".format(self.port)

    @property
    def is_open(self):
        return super().is_open and self._ser and self._ser.isOpen()

    def open(self):
        self.log(f'Trying to open serial port {self.port}', level=LogLevel.DEBUG)
        self._ser = Serial(
            port=self.port,
            baudrate=self.baud,
            timeout=self._timeout
        )

        self.interactor.open(console_fd=self._ser.fileno())

        if not self.is_open:
            raise RuntimeError(f'Failed to open serial port {self.port}')

        self.log(f'Init serial {self.port} success', level=LogLevel.DEBUG)
        return

    def close(self):
        if not self.is_open:
            return

        self._ser.flush()
        super().close()
        self._ser.close()
        self._ser = None
        self.log("Closed serial", level=LogLevel.DEBUG)

    def interact(self, exit_char=None):
        '''
        Take interactive control of a SerialConsole.
        The intention is that this be used from the command line.
        To exit the terminal press the exit character.
        You can set the exit character with @exit_char, default is "¬".
        '''
        if not self.is_open:
            self.open()

        exit_char = exit_char or '¬'

        self.log('Starting interactive console')
        print(f'Press {exit_char} to exit')

        com = self._logging_Nanocom(self.raw_logfile, self._ser,
                                    exit_character=exit_char)

        com.start()
        try:
            com.join()
        except KeyboardInterrupt:
            pass
        finally:
            self.log('Exiting interactive console...')
            com.close()

    class _logging_Nanocom(Nanocom):
        '''
        This class just slightly modifies Nanocom to get it to log
        received data to a file.
        This is done so that the text from the interactive session
        is written to the raw logfile, along with everything else.
        The reader() method is copy-pasted from Nanocom and modified.
        '''

        def __init__(self, logfile, *args, **kwargs):
            self.logfile = logfile
            Nanocom.__init__(self, *args, **kwargs)

        def reader(self):
            try:
                while self.alive:
                    data = self.serial.read(self.serial.in_waiting or 1)
                    if data:
                        self.console.write_bytes(data)
                        with open(self.logfile, 'ab') as f:
                            f.write(data)
            except Exception:
                self.alive = False
                self.console.cancel()
                raise
