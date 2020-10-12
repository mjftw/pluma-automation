class TestingException(Exception):
    pass


class TaskFailed(TestingException):
    pass


class AbortTesting(TestingException):
    pass
