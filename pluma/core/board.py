import time

from .baseclasses import HardwareBase, ConsoleBase
from .dataclasses import SystemContext
from .exceptions import ConsoleExceptionKeywordReceivedError


class BoardError(Exception):
    pass


class BoardBootValidationError(BoardError):
    pass


class BoardFieldInstanceIsNoneError(BoardError):
    pass


class Board(HardwareBase):
    def __init__(self, name, power=None, hub=None, storage=None, console=None,
                 bootstr=None, boot_max_s=None, logfile=None,
                 login_user_match=None, login_pass_match=None,
                 system: SystemContext = None):
        self.name = name
        self.power = power
        self.storage = storage
        self.hub = hub

        self._current_console_name = None
        self._consoles = None
        self.consoles = console
        self.system = system or SystemContext()

        self.login_user_match = login_user_match or 'login:'
        self.login_pass_match = login_pass_match or 'Password:'
        self.bootstr = bootstr or self.login_user_match
        self.boot_max_s = boot_max_s or 60

        self.last_boot_len = None
        self.booted_to_prompt = False

        self.log_recurse = True

    def __repr__(self):
        return 'Board[{}]'.format(self.name)

    @property
    def console(self) -> ConsoleBase:
        if self._current_console_name:
            return self.consoles[self._current_console_name]
        else:
            return None

    @console.setter
    def console(self, new_console: ConsoleBase):
        if not self.consoles or new_console not in self.consoles.values():
            self.consoles = new_console
        else:
            for name, console in self.consoles.items():
                if console is new_console:
                    self._current_console_name = name
                    break

    @property
    def consoles(self) -> dict:
        return self._consoles

    @consoles.setter
    def consoles(self, new_consoles) -> dict:
        if isinstance(new_consoles, ConsoleBase):
            new_consoles = {'main': new_consoles}
        elif not isinstance(new_consoles, dict) and new_consoles is not None:
            raise ValueError(
                "Error settings consoles: Must be a ConsoleBase or dict")

        if new_consoles:
            # Set current console to the first passed, in the previous one
            # is not present
            if self._current_console_name not in new_consoles.keys():
                self._current_console_name = next(
                    iter(new_consoles)) if new_consoles else None

            for console_name, console in new_consoles.items():
                if not isinstance(console, ConsoleBase):
                    raise ValueError(f'Console "{console_name}" ({console}) is null or '
                                     'not an instance of ConsoleBase')

        self._consoles = new_consoles

    def get_console(self, console_name: str = None) -> ConsoleBase:
        '''Get a specific console from the Board.'''
        if console_name:
            return self.consoles.get(console_name)
        else:
            return self.console

    def reboot_and_validate(self, override_bootstr=None, override_timeout=None,
                            exception_bootstr=None):
        timeout = override_timeout or self.boot_max_s
        bootstr = override_bootstr or self.bootstr

        if self.power is None:
            raise BoardFieldInstanceIsNoneError('"power" instance is not set')

        if self.console is None:
            raise BoardFieldInstanceIsNoneError(
                '"console" instance is not set')

        # If we have set a prompt, add this to bootstr search
        prompt = self.system.prompt_regex
        if prompt:
            if not bootstr:
                bootstr = prompt
            elif isinstance(bootstr, list):
                bootstr.append(prompt)
            else:
                bootstr = [bootstr, prompt]

        if not bootstr:
            raise BoardBootValidationError(
                "Cannot validate boot. No bootstring given")

        self.booted_to_prompt = False
        self.last_boot_len = None
        self.power.reboot()
        start_time = time.time()
        try:
            (__, matched) = self.console.send_and_expect(
                match=bootstr,
                excepts=exception_bootstr,
                send_newline=False,
                timeout=timeout,
                sleep_time=5)
        except ConsoleExceptionKeywordReceivedError as e:
            raise BoardBootValidationError('Matched exception keyword: {}'.format(
                str(e)))

        if not matched:
            raise BoardBootValidationError(
                "Did not get bootstring: {}".format(bootstr))

        self.last_boot_len = round(time.time() - start_time, 2)
        self.log(f'Boot success. Matched [{matched}]')

        prompt = self.system.prompt_regex
        if prompt and matched == prompt:
            self.booted_to_prompt = True

        return self.last_boot_len

    def login(self):
        if self.console is None:
            raise BoardFieldInstanceIsNoneError(
                '"console" instance is not set')

        if self.booted_to_prompt:
            self.log('Booted to prompt. Not need to log in')
            return

        self.console.login(
            username=self.system.credentials.login,
            password=self.system.credentials.password,
            username_match=self.login_user_match,
            password_match=self.login_pass_match,
            success_match=self.system.prompt_regex
        )


def get_board_by_name(boards, name):
    invalid_boards = [b for b in boards if not isinstance(b, Board)]
    if invalid_boards:
        raise RuntimeError(
            f'All boards must be of type Board! Invalid: {invalid_boards}')

    filtered_boards = [b for b in boards if b.name == name]
    if len(filtered_boards) <= 0:
        raise RuntimeError(
            f'No boards found with name [{name}]. Available: {[b.name for b in boards]}')
    if len(filtered_boards) > 1:
        raise RuntimeError(f'Multiple boards found with name [{name}]')

    return filtered_boards[0]
