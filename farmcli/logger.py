import logging

style_map = {
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'purple': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[3m',
    'bold': '\033[1m',
    'normal': '\033[0m'
}


class PlumaLogger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        self.enabled = True
        self.debug_enabled = False

    @staticmethod
    def logger():
        global logger
        return logger

    def set_enabled(self, enabled):
        self.enabled = enabled

    def set_debug_enabled(self, enabled):
        self.debug_enabled = enabled

    def debug(self, message):
        if not self.enabled or not self.debug_enabled:
            return

        self.log(message)

    def warning(self, message):
        if not self.enabled or not self.debug_enabled:
            return

        self.log(message, color='yellow')

    def error(self, message):
        if not self.enabled or not self.debug_enabled:
            return

        self.log(message, color='red')

    def log(self, message, color=None, bold=False):
        if not self.enabled:
            return

        if color in style_map:
            message = '{}{}{}'.format(
                style_map[color],
                message,
                style_map['normal']
            )
        if bold:
            message = '{}{}{}'.format(
                style_map['bold'],
                message,
                style_map['normal']
            )

        print(message)


logger = PlumaLogger()
