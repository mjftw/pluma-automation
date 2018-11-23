import datetime

from .test import deferred_function

class TestMustBeInSuite(Exception):
    pass


@deferred_function
def sc_run_n_iterations(suite, ntimes):
    return suite.num_iterations_run < ntimes


@deferred_function
def sc_time_in_range(suite, start_hour, end_hour):
    now = datetime.datetime.now()
    return (start_hour <= now.hour and now.hour < end_hour)


@deferred_function
def tt_log_stats(suite, board):
    if suite is None:
        raise TestMustBeInSuite

    board.log("Test #: {}, pass #: {}, fail #: {}".format(
        suite.num_tests_run,
        suite.num_tests_pass,
        suite.num_tests_fail
        ))


@deferred_function
def ss_boot(__, board, boot_string, iterations):
    board.log("---- Beggining boot test with boot string '{}' ---- ".format(
        boot_string))


@deferred_function
def ss_log_test_plan(suite, board):
    message = "Starting test suite:\n"
    if suite.setup:
        message += "\t{}: {}\n".format(
            suite.setup['name'],
            suite.setup['str'])
    if suite.run_condition:
        message += "\t{}: {}\n".format(
            suite.run_condition['name'],
            suite.run_condition['str'])
    if suite.report:
        message += "\t{}: {}\n".format(
            suite.report['name'],
            suite.report['str'])
    message += str(suite.tests)
    board.log(message)


@deferred_function
def sr_log_test_results(suite, board):
    print("In func {}".format(__name__))
    message = "Test suite results: \n".format(suite.name)
    for test in suite.tests_passed:
        message += "\t{}: PASS\n".format(
            test.body['str'])
    for test in suite.tests_failed:
        message += "\t{}: FAIL\n".format(
            test.body['str'])
    message += "Total tests:\n"
    message += "\tRun = {}\n".format(suite.num_tests_run)
    message += "\tPass = {}\n".format(suite.num_tests_pass)
    message += "\tFail = {}\n".format(suite.num_tests_fail)
    message += "Total iterations:\n"
    message += "\tRun = {}\n".format(suite.num_iterations_run)
    message += "\tPass = {}\n".format(suite.num_iterations_pass)
    message += "\tFail = {}\n".format(suite.num_iterations_fail)
    board.log(message)

@deferred_function
def tb_boot(__, board, boot_str="linux"):
    board.log("Starting linux boot test with boot string \"{}\"".format(boot_str))
    board.power.restart()
    (__, matched) = board.console.send(cmd="", recieve=True, match=boot_str)
    if matched:
        return True
    else:
        board.log("TIMEOUT waiting for boot string...")
        return False


@deferred_function
def tb_login(__, board, user="root", pw=None, prompt="#"):
    board.log("Starting login test with user={}, pass={}, prompt={}".format(
        user, pw, prompt
    ))
    (__, matched) = board.console.send(cmd="", recieve=True, match=["login", "Password", prompt])
    if not matched:
        return False
    if matched == "login":
        (__, matched) = board.console.send(cmd=user, recieve=True, match=["login", "Password", prompt])
    if matched == "Password":
        if not pw:
            return False
        (__, matched) = board.console.send(cmd=pw, recieve=True, match=["login", "Password", prompt])
    if matched == prompt:
        return True
    else:
        return False

