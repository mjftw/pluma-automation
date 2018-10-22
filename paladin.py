import datetime
import os


from farmcore import farm
from farmutils.doemail import Email
from farmutils.test import TestSuite, Test, test_func, testlib

def main():
    hub = farm.Hub('1-3')
    paladin = farm.Board(
        name='paladin',
        power=farm.PowerRelay(
            hub=hub,
            on_seq=[(1, 'A'), (2, 'B'), "100ms", (2, 'A'), "100ms", (2, 'B')],
            off_seq=[(1, 'B'), (2, 'B'), "5s"]
        ),
        hub=hub,
        sdmux=None,
        logfile="paladin.log"
    )
    paladin.console.logon = False
    paladin.power.logon = True

    boot_string = "login"

    # When running on a beaglebone the TZ is not set, so these are UTC times and you need to take account of any DST adjustment.
    start_hour = 9
    stop_hour = 10

    suite = TestSuite(
        name="Paladin"
        setup_func=testlib.ss_boot(paladin, boot_string),
        tests=[
            testlib.tb_boot(paladin, boot_string),
            testlib.tb_login(paladin, user="root", prompt="#")
        ],
        report_func=send_test_report(paladin),
        run_condition_func=testlib.sc_time_in_range(9, 10),
        run_forever=True,
    )

    suite.run()


@test_func
def send_test_report(suite, board):
    board.log("Sending test report")

    timestr = datetime.datetime.now().strftime("%y-%m-%d_%H:%M:%S")
    os.rename("paladin.log", "paladin_{}.log".format(timestr))

    body = """ --------- Automated Paladin boot test report ---------
               Boot attempts: {}, Pass: {}, Fail: {}""".format(
                   suite.num_tests_run,
                   suite.num_tests_pass,
                   suite.num_tests_fail
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


if __name__ == '__main__':
    main()
