import datetime

from .test import test_func

class TestMustBeInSuite(Exception):
    pass


@test_func
def sc_run_n_iterations(suite, ntimes):
    return suite.num_iterations_run < ntimes


@test_func
def sc_time_in_range(suite, start_hour, end_hour):
    now = datetime.datetime.now()
    return (start_hour <= now.hour and now.hour < end_hour)


@test_func
def test_body(suite, board, boot_string):
    success = False
    board.power.restart()
    try:
        board.console.send("", True, boot_string, False)
        success = True
    except farm.TimeoutNoRecieve:
        board.log("TIMEOUT waiting for boot string...")

    return success


@test_func
def tt_log_stats(suite, board, test_no, pass_no, fail_no):
    if suite is None:
        raise TestMustBeInSuite

    board.log("Test #: {}, pass #: {}, fail #: {}".format(
        suite.num_tests_run,
        suite.num_tests_pass,
        suite.num_tests_fail
        ))


@test_func
def ss_boot(suite, board, boot_string, iterations):
    board.log("---- Beggining boot test over {} iterations with boot string '{}' ---- ".format(
        iterations, boot_string))
