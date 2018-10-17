import sys
sys.path.append('/home/phil/farm/farm-core/farmcore')
sys.path.append('/home/phil/farm/farm-core/farmutils')
import time
import datetime
import os


from farmcore import farm
from farmutils.doemail import Email


def main():
    hub = farm.Hub('1-3')
    paladin = farm.Board(
        name='paladin',
        power=farm.PowerRelay(
            hub=hub,
            on_seq=[(1, 'A'), (2, 'B'), "100ms", (2, 'A'), "100ms", (2, 'B')],
            off_seq=[(1, 'B'), (2, 'B'), "5000ms"]
        ),
        hub=hub,
        sdmux=None,
        logfile="paladin.log"
        #logfile=None
    )
    paladin.console.logon = False
    paladin.power.logon = True

    boot_test(paladin, 10000)


def time_in_range(start_hour, end_hour):
    now = datetime.datetime.now()
    return (start_hour <= now.hour and now.hour < end_hour)


def send_test_report(board, test_no, pass_no, fail_no):
    board.log("Sending test report")

    body = """ --------- Automated Paladin boot test report ---------
               Boot attempts: {}, Pass: {}, Fail: {}""".format(
                   test_no, pass_no, fail_no
               )
    Email(
       sender="probinson@witekio.com",
       to="probinson@witekio.com",
       cc=["mwebster@witekio.com", "elangley@witekio.com", "asison@witekio.com"],
       subject="Automated Paladin boot test report",
       body=body,
       files=[board.logfile],
       smtp_authfile='./smtp.auth'
    ).send()


def boot_test(board, itterations):

    boot_string = "login"

    pass_no = 0
    fail_no = 0
    test_no = 0

    board.log("---- Beggining boot test over {} itterations with boot string '{}' ---- ".format(
        itterations, boot_string)
    )

    # When running on a beaglebone the TZ is not set, so these are UTC times and you need to take account of any DST adjustment.
    start_hour = 9
    stop_hour = 10

    while True:
        while not time_in_range(start_hour, stop_hour):
            test_no += 1
            board.power.restart()
            try:
                board.console.send("", True, boot_string, False)
                pass_no += 1

            except farm.TimeoutNoRecieve:
                board.log("TIMEOUT waiting for boot string...")
                fail_no += 1

            board.log("Test #: {}, pass #: {}, fail #: {}".format(
                test_no, pass_no, fail_no)
            )

        send_test_report(board, test_no, pass_no, fail_no)
        # reset metrics and archive the log file
        pass_no = 0
        fail_no = 0
        test_no = 0
        timestr = datetime.datetime.now().strftime("%y-%m-%d_%H:%M:%S")
        os.rename("paladin.log", "paladin_{}.log".format(timestr))

        while time_in_range(start_hour, stop_hour):
            time.sleep(600)



if __name__ == '__main__':
    main()
