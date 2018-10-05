import time
import datetime


from farmcore import farm
from farmutils.doemail import Email


def main():
    hub = farm.Hub('3-3')
    paladin = farm.Board(
        name='paladin',
        power=farm.PowerRelay(
            hub=hub,
            on_seq=[(1, 'A'), (2, 'B'), "100ms", (2, 'A'), "100ms", (2, 'B')],
            off_seq=[(1, 'B'), (2, 'B')]
        ),
        hub=hub,
        sdmux=None,
        # logfile="paladin.log"
        logfile=None
    )
    paladin.console.logon = False
    paladin.power.logon = True

    boot_test(paladin, 10000)


def time_in_range(start_hour, end_hour):
    now = datetime.datetime.now()
    return (start_hour <= now.hour and now.hour < end_hour)


def send_test_report(board):
    board.log("Sending test report")

    body = """ --------- Automated Paladin boot test report ---------
               Boot attempts: {}, Pass: {}, Fail: {}""".format(
                   test_no, pass_no, fail_no
               )
    Email(
       sender="mwebster@witekio.com",
       to="mwebster@witekio.com",
       cc=["probinson@witekio.com", "elangley@witekio.com", "asison@witekio.com"],
       subject="Automated Paladin boot test report",
       body=body,
       files=[board.logfile],
       smtp_authfile='./smtp.auth'
    ).send()


def boot_test(board, itterations):

    boot_string = "SoloProtect"

    pass_no = 0
    fail_no = 0
    test_no = 0

    board.log("---- Beggining boot test over {} itterations with boot string '{}' ---- ".format(
        itterations, boot_string)
    )

    start_hour = 6
    stop_hour = 18

    while True:
        while not time_in_range(start_hour, stop_hour):
            test_no += 1
            board.power.restart()
            try:
                board.console.send("", True, boot_string)
                pass_no += 1

            except farm.TimeoutNoRecieve:
                board.log("TIMEOUT waiting for boot string...")
                fail_no += 1

            board.log("Test #: {}, pass #: {}, fail #: {}".format(
                test_no, pass_no, fail_no)
            )

        send_test_report(board)

        while time_in_range(start_hour, stop_hour):
            time.sleep(600)



if __name__ == '__main__':
    main()