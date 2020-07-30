from farmcore.baseclasses import Singleton

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


class PlumaLogger(Singleton):
    def __init__(self):
        self.enabled = True
        self.debug_enabled = False

    def log(self, message, color=None, bold=False):
        if not self.enabled:
            return

        self._log(message, color, bold)

    def debug(self, message):
        if not self.enabled or not self.debug_enabled:
            return

        self._log(message)

    def info(self, message):
        if not self.enabled:
            return

        self._log(message)

    def warning(self, message):
        if not self.enabled:
            return

        self._log(message, color='yellow')

    def error(self, message):
        self._log(message, color='red')

    def _log(self, message, color=None, bold=False):
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
