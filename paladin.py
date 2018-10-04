import time

from farmcore import farm


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

def boot_test(board, itterations):

    boot_string = "SoloProtect"

    pass_no = 0
    fail_no = 0
    test_no = 0

    board.log("---- Beggining boot test over {} itterations with boot string '{}' ---- ".format(
        itterations, boot_string)
    )

    while test_no < itterations:
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

    board.log("---- Finished tests ----")

if __name__ == '__main__':
    main()