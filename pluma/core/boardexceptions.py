
class BoardError(Exception):
    pass


class BoardBootValidationError(BoardError):
    pass


class BoardFieldInstanceIsNoneError(BoardError):
    pass
