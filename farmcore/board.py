from pexpect import TIMEOUT, EOF


from .farmclass import Farmclass
from .serialconsole import SerialConsole
from .console import ExceptionKeywordRecieved


DEFAULT_LOGFILE = object()


class BootValidationError(Exception):
    pass


class LoginError(Exception):
    pass


class Board(Farmclass):
    def __init__(self, name, power=None, hub=None, muxpi=None,
            storage=None, console=None,
            login_user='root', login_pass=None,
            bootstr=None, prompt=None, logfile=DEFAULT_LOGFILE):
        self.name = name

        self.muxpi = muxpi
        if self.muxpi:
            self.muxpi.attach_board(self)
        elif power and hub:
            self.power = power
            self.hub = hub
            self.storage = storage
            self.console = console or SerialConsole(hub.get_serial()['devnode'], 115200)
        else:
            #TODO: This is not always the case as sometimes we may not use
            #    a hub or control power. Allow this use case
            raise TypeError("__init__() must set argument 'muxpi' or both 'power' and 'hub'")

        self.prompt = prompt
        self.login_user = login_user
        self.login_pass = login_pass
        self.login_user_match = 'login:'
        self.login_pass_match = 'Password:'
        self.bootstr = bootstr or self.login_user_match

        self.log_reccurse = True

        if logfile is DEFAULT_LOGFILE:
            self.log_file = "/tmp/board_{}.log".format(self.name)
        else:
            self.log_file = logfile

    def __repr__(self):
        return 'Board[{}]'.format(self.name)

    def reboot_and_validate(self, override_boostr=None, override_timeout=None,
            exception_bootstr=None):
        timeout = override_timeout or 60
        bootstr = override_boostr or self.bootstr
        if not bootstr:
            raise BootValidationError("Cannot validate boot. Not bootstring given")

        self.power.reboot()
        try:
            (__, matched) = self.console.send(match=bootstr,
                send_newline=False, timeout=timeout, excepts=exception_bootstr)
        except ExceptionKeywordRecieved as e:
            raise BootValidationError('Matched exception keyword: {}'.format(
                str(e)))

        if matched is False or matched is TIMEOUT or matched is EOF:
            raise BootValidationError("Did not get bootstring: {}".format(bootstr))

    def login(self):
        self.console.login(
            username=self.login_user,
            password=self.login_pass,
            username_match=self.login_user_match,
            password_match=self.login_pass_match,
            success_match=self.prompt
        )