from farmtest.unittest import UnitTestSuite, UnitTest, deferred_function
from farmtest import unittestlib
from farmcore.farmobj_mock import FarmobjMock


@deferred_function
def my_testbody(suite, arg1):
    print("Test body, arg1={}".format(arg1))
    return True

@deferred_function
def my_fsetup(suite):
    print("Test setup")

@deferred_function
def my_ssetup(suite, arg1, arg2, arg3, arg4, arg5):
    print("in my_ssetup: args={}".format(locals()))

@deferred_function
def my_fteardown(suite):
    print("Num tests run = {}".format(test.suite.num_tests_run))


def my_sreport(suite):
    print("Suite report:")
    print("num_iterations_run={}".format(suite.num_iterations_run))
    print("num_iterations_pass={}".format(suite.num_iterations_pass))
    print("num_iterations_fail={}".format(suite.num_iterations_fail))


@deferred_function
def foo(bar, barbar):
    print(bar, barbar)


def main():
    mock_board = FarmobjMock()

    my_test = UnitTest(
        fsetup=my_fsetup(),
        fbody=my_testbody(10),
        fteardown=unittestlib.tt_log_stats(mock_board)
    )

    my_suite = UnitTestSuite(
        tests=my_test,
        setup_func=unittestlib.ss_log_test_plan(mock_board),
        report_func=unittestlib.sr_log_test_results(mock_board),
        run_condition_func=unittestlib.sc_run_n_iterations(3),
        report_n_iterations=3,
    )

    my_suite.run()


if __name__ == "__main__":
    main()
