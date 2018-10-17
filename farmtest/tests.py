import unittest

from farmcore import farm


class BootTest(unittest.TestCase):
    def __init__(self, board, bootstring):
        self.board = board
        self.bootstring = bootstring

    def setUp(self):
        print("Setup")
        self.board.log("---- Beggining boot tests on {} board with boot string '{}' ---- ".format(
            self.board.name, self.bootstring)
        )

    def test_boot(self):
        self.board.power.restart()
        try:
            self.board.console.send("", True, self.boot_string)
            self.board.log("Boot test: PASS")
        except farm.TimeoutNoRecieve:
            self.board.log("Boot test: FAIL")
            self.fail("TIMEOUT waiting for boot string...")

    def tearDown(self):
        print("Teardown")
        self.board.log("---- Finished tests ----")
        board.log("Sending test report")

        Email(
            sender="mwebster@witekio.com",
            to="mwebster@witekio.com",
            # cc=["probinson@witekio.com", "elangley@witekio.com", "asison@witekio.com"]
            subject="Automated Paladin boot test report",
            body=body,
            files=[board.logfile],
            smtp_authfile='./smtp.auth'
        ).send()
