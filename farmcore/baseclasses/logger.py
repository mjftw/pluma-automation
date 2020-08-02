from .singleton import Singleton

COLOR_STYLES = {
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'purple': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[3m'
}
STYLE_NORMAL = '\033[0m'
STYLE_BOLD = '\033[1m'


class PlumaLogger(Singleton):
    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
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
        style_reset = STYLE_NORMAL
        if color:
            if color in COLOR_STYLES:
                message = f'{COLOR_STYLES[color]}{message}{style_reset}'
                style_reset = ''
            else:
                raise ValueError(
                    f'Invalid color {color}. Supported colors: {COLOR_STYLES}')

        if bold:
            message = f'{STYLE_BOLD}{message}{style_reset}'

        print(message)
