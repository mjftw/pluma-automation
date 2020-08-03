class Singleton:
    '''Simple Singleton class.

    Ensures that only one object of the class is created.
    Use `self._initialized` attribute to set and verify if
    the `__init__` constructor was already executed.
    '''

    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
            cls.__instance._initialized = False
        return cls.__instance
