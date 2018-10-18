import datetime


""" Suite run conditions """

def sc_run_n_iterations(ntimes):
    def suite_run_condition(suite, ntimes):
        return suite.num_iterations_run < ntimes
    return (suite_run_condition, ntimes)

def sc_time_in_range(start_hour, end_hour):
    def suite_run_condition(suite, start_hour, end_hour):
        now = datetime.datetime.now()
        return (start_hour <= now.hour and now.hour < end_hour)
    return (suite_run_condition, start_hour, end_hour)

""" Tests """

def tb_boot(board, boot_string):
    def test_body(board, boot_string):
        success = False
        board.power.restart()
        try:
            board.console.send("", True, boot_string, False)
            success = True
        except farm.TimeoutNoRecieve:
            board.log("TIMEOUT waiting for boot string...")

        return success
    return (test_body, board, boot_string)


def tt_log_stats(board, test_no, pass_no, fail_no):
    def test_teardown(board, test_no, pass_no, fail_no):
        board.log("Test #: {}, pass #: {}, fail #: {}".format(
            test_no, pass_no, fail_no))
    return (test_teardown, board, test_no, pass_no, fail_no)


def ss_boot(board, boot_string, iterations):
    def suite_setup(suite, board, boot_string, iterations):
        board.log("---- Beggining boot test over {} iterations with boot string '{}' ---- ".format(
            iterations, boot_string))
    return (suite_setup, board, boot_string, iterations)
