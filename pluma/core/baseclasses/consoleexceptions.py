class ConsoleError(Exception):
    pass


class ConsoleCannotOpenError(ConsoleError):
    pass


class ConsoleLoginFailedError(ConsoleError):
    pass


class ConsoleExceptionKeywordReceivedError(ConsoleError):
    pass


class ConsoleInvalidJSONReceivedError(ConsoleError):
    pass
