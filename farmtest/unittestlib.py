import datetime
import time

from .unittest import deferred_function

#TODO: Revist with better name for this

class TestMustBeInController(Exception):
    pass


@deferred_function
def sc_run_n_iterations(TestController, ntimes):
    return TestController.stats['num_iterations_run'] < ntimes


@deferred_function
def sc_time_in_range(start_hour, end_hour):
    now = datetime.datetime.now()
    return (start_hour <= now.hour and now.hour < end_hour)


@deferred_function
def sc_run_daily_at_hour(TestController, start_hour):
    data_key = 'sc_run_daily_at_hour:run_dates'

    now = datetime.datetime.now()
    date_now = now.strftime("%Y/%m/%d")

    if start_hour <= now.hour:
        if not data_key in TestController.data:
            TestController.data[data_key] = [date_now]
            return True

        if date_now not in TestController.data[data_key]:
            TestController.data[data_key].append(date_now)
            return True

    return False


@deferred_function
def tt_log_stats(TestController, board):
    if TestController is None:
        raise TestMustBeInSController
    board.log("Test #: {}, pass #: {}, fail #: {}".format(
        TestController.stats['num_tests_run'],
        TestController.stats['num_tests_pass'],
        TestController.stats['num_tests_fail']
        ))


@deferred_function
def ss_log_test_plan(TestController, board):
    message = "Starting test TestController:\n"
    if TestController.setup:
        message += "\t{}: {}\n".format(
            TestController.setup['name'],
            TestController.setup['str'])
    if TestController.run_condition:
        message += "\t{}: {}\n".format(
            TestController.run_condition['name'],
            TestController.run_condition['str'])
    if TestController.report:
        message += "\t{}: {}\n".format(
            TestController.report['name'],
            TestController.report['str'])
    message += str(TestController.tests)
    board.log(message)


@deferred_function
def sr_log_test_results(TestController, board):
    print("In func {}".format(__name__))
    message = "Test TestController results: \n".format(TestController.name)
    for test in TestController.tests_passed:
        message += "\t{}: PASS\n".format(
            test.body['str'])
    for test in TestController.tests_failed:
        message += "\t{}: FAIL\n".format(
            test.body['str'])
    message += "Total tests:\n"
    message += "\tRun = {}\n".format(TestController.stats['num_tests_run'])
    message += "\tPass = {}\n".format(TestController.stats['num_tests_pass'])
    message += "\tFail = {}\n".format(TestController.stats['num_tests_fail'])
    message += "Total iterations:\n"
    message += "\tRun = {}\n".format(TestController.stats['num_iterations_run'])
    message += "\tPass = {}\n".format(TestController.stats['num_iterations_pass'])
    message += "\tFail = {}\n".format(TestController.stats['num_iterations_fail'])
    board.log(message)


@deferred_function
def sleep_and_notify(duration, unit, mode, log_func=print):
    log_func("Now waiting {} {}...".format(
        duration, unit))
    for duration in reversed(range(1, duration+1)):
        log_func("{} {} to go...".format(duration, unit))
        if unit == 'hours':
            time.sleep(60*60)
        if unit == 'minutes':
            time.sleep(60)
        if unit == 'seconds':
            time.sleep(1)


@deferred_function
def console_is_alive(console):
    try:
        return console.check_alive()
    except KeyboardInterrupt as e:
        raise e
    except InterruptedError as e:
        raise e
    except Exception as e:
        return False