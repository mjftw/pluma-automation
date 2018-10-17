from farmutils.test import TestSuite, test


@test
def my_test():
    print("Test body")
    return True


@my_test.setup
def my_setup():
    print("Test setup")


@my_test.teardown
def my_teardown():
    print("Test teardown")


def suite_setup(suite, *args):
    print("Suite setup called with: {}".format(*args))


def suite_report(suite):
    print("Suite report:")
    print("num_iterations_run={}".format(suite.num_iterations_run))
    print("num_iterations_pass={}".format(suite.num_iterations_pass))
    print("num_iterations_fail={}".format(suite.num_iterations_fail))


def suite_run_condition(suite, ntimes):
    return suite.num_iterations_run < ntimes


def main():
    suite = TestSuite(
        tests=my_test,
        setup_func=(suite_setup, "Hello!", 10),
    )

    suite.run_condition_func = (suite_run_condition, 5)
    suite.report_func = suite_report

    suite.run()

if __name__ == "__main__":
    main()
