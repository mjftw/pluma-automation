from farmutils.test import TestSuite, Test


@Test
def my_test():
    print("Test body")
    return True


@my_test.setup
def my_setup():
    print("Test setup")


@my_test.teardown
def my_teardown():
    print("Test teardown")


def my_fsetup(arg1):
    print("In my_fsetup, arg1={}".format(arg1))


def my_fbody():
    print("In my_fbody")


def my_fteardown():
    print("In my_fteardown")


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
    my_test()

    suite = TestSuite(
        tests=Test(
            fbody=my_fbody,
            fsetup=(my_fsetup, 12343),
            fteardown=my_fteardown
        ),
        setup_func=(suite_setup, "Hello!", 10),
    )

    suite.run_condition_func = (suite_run_condition, 3)
    suite.report_func = suite_report

    suite.run()

if __name__ == "__main__":
    main()
