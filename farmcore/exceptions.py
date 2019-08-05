from .baseclasses.consolebase import ConsoleError,\
    ConsoleCannotOpen, ConsoleLoginFailed, ConsoleExceptionKeywordRecieved,\
    ConsoleInvalidJSONRecieved
from .baseclasses.storagebase import StorageError
from .board import BoardError, BoardBootValidationError
from .modem import ModemError
from .multimeter import MultimeterError, MultimeterInvalidKeyPress,\
    MultimeterMeasurementError, MultimeterDecodeError
from .pdu import PDUError, PDUInvalidPort, PDURequestError
from .usb import USBError, USBNoDevice
from .muxpi import MuxPiError