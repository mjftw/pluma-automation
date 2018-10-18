from farmutils.test import TestSuite, Test, test_func
from farmutils import testlib

@test_func
def my_testbody(test, arg1):
    print("Test body, arg1={}".format(arg1))
    return True

@test_func
def my_fsetup(test):
    print("Test setup")

@test_func
def my_ssetup(suite, arg1, arg2, arg3, arg4, arg5):
    print("in my_ssetup: args={}".format(locals()))

@test_func
def my_fteardown(test):
    print("Num tests run = {}".format(test.suite.num_tests_run))


def my_sreport(suite):
    print("Suite report:")
    print("num_iterations_run={}".format(suite.num_iterations_run))
    print("num_iterations_pass={}".format(suite.num_iterations_pass))
    print("num_iterations_fail={}".format(suite.num_iterations_fail))

def main():
    my_test = Test(
        fsetup=my_fsetup,
        fbody=my_testbody(10),
        fteardown=my_fteardown()
    )

    my_suite = TestSuite(
        tests=my_test,
        setup_func=my_ssetup("Hello", 1, 9, arg5=["mylist"], arg4=123),
        report_func=my_sreport,
        run_condition_func=testlib.sc_run_n_iterations(6),
        report_n_iterations=3,
    )

    my_suite.run()

if __name__ == "__main__":
    main()
