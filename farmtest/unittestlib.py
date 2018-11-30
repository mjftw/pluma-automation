import datetime

from .unittest import deferred_function


class TestMustBeInSuite(Exception):
    pass


@deferred_function
def sc_run_n_iterations(suite, ntimes):
    return suite.num_iterations_run < ntimes


@deferred_function
def sc_time_in_range(start_hour, end_hour):
    now = datetime.datetime.now()
    return (start_hour <= now.hour and now.hour < end_hour)

@deferred_function
def sc_run_daily_at_hour(suite, start_hour):
    data_key = 'sc_run_daily_at_hour:run_dates'

    now = datetime.datetime.now()
    date_now = now.strftime("%Y/%m/%d")

    if start_hour <= now.hour:
        if not data_key in suite.data:
            suite.data[data_key] = [date_now]
            return True

        if date_now not in suite.data[data_key]:
            suite.data[data_key].append(date_now)
            return True

    return False


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
