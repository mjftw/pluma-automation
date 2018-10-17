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


def suite_setup(*args):
    print("Suite setup. {}".format(*args))


def suite_report():
    print("Suite report")


def main():
    suite = TestSuite(
        [my_test, my_test],
        (suite_setup, "Hello!", 10),
        suite_report
    )

    suite.run()


if __name__ == "__main__":
    main()
