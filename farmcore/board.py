import time
from pexpect import TIMEOUT, EOF


from .baseclasses import Farmclass
from .exceptions import ConsoleExceptionKeywordRecieved


DEFAULT_LOGFILE = object()


class BoardError(Exception):
    pass


class BoardBootValidationError(BoardError):
    pass


class Board(Farmclass):
    def __init__(self, name, power=None, hub=None, muxpi=None,
            storage=None, console=None,
            login_user='root', login_pass=None,
            bootstr=None, boot_max_s=None,
            prompt=None, logfile=DEFAULT_LOGFILE):
        self.name = name

        self.power = power
        self.storage = storage
        self.console = console
        self.hub = hub
        self.muxpi = muxpi

        if self.muxpi:
            self.muxpi.attach_board(self)

        self.prompt = prompt
        self.login_user = login_user
        self.login_pass = login_pass
        self.login_user_match = 'login:'
        self.login_pass_match = 'Password:'
        self.bootstr = bootstr or self.login_user_match
        self.boot_max_s = boot_max_s or 60

        self.last_boot_len = None
        self.booted_to_prompt = False

        self.log_reccurse = True

        if logfile is DEFAULT_LOGFILE:
            self.log_file = "/tmp/board_{}.log".format(self.name)
        else:
            self.log_file = logfile

    def __repr__(self):
        return 'Board[{}]'.format(self.name)

    def reboot_and_validate(self, override_boostr=None, override_timeout=None,
            exception_bootstr=None):
        timeout = override_timeout or self.boot_max_s
        bootstr = override_boostr or self.bootstr

        # If we have set a prompt, add this to bootstr search
        if self.prompt:
            if not bootstr:
                bootstr = self.prompt
            elif isinstance(bootstr, list):
                bootstr.append(self.prompt)
            else:
                bootstr = [bootstr, self.prompt]

        if not bootstr:
            raise BoardBootValidationError("Cannot validate boot. Not bootstring given")

        self.last_boot_len = None
        self.power.reboot()
        start_time = time.time()
        try:
            (__, matched) = self.console.send(
                match=bootstr,
                send_newline=False,
                timeout=timeout,
                sleep_time=1,
                excepts=exception_bootstr)
        except ConsoleExceptionKeywordRecieved as e:
            raise BoardBootValidationError('Matched exception keyword: {}'.format(
                str(e)))

        if matched is False or matched is TIMEOUT or matched is EOF:
            raise BoardBootValidationError("Did not get bootstring: {}".format(bootstr))

        self.last_boot_len = round(time.time() - start_time, 2)

        self.log('Boot success. Matched [{}]'.format(matched))

        if self.prompt and matched == self.prompt:
            self.booted_to_prompt = True

    def login(self):
        if self.booted_to_prompt:
            self.log('Booted to prompt. Not need to log in')
            return

        self.console.login(
            username=self.login_user,
            password=self.login_pass,
            username_match=self.login_user_match,
            password_match=self.login_pass_match,
            success_match=self.prompt
        )


def get_board_by_name(boards, name):
    invalid_boards = [b for b in boards if not isinstance(b, Board)]
    if invalid_boards:
        raise RuntimeError(f'All boards must be of type Board! Invalid: {invalid_boards}')

    filtered_boards = [b for b in boards if b.name == name]
    if len(filtered_boards) <= 0:
        raise RuntimeError(
            f'No boards found with name [{name}]. Avialable: {[b.name for b in boards]}')
    if len(filtered_boards) > 1:
        raise RuntimeError(f'Multiple boards found with name [{name}]')

    return filtered_boards[0]
