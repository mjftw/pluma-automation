import time
import json
from datetime import datetime
from copy import deepcopy

from .unittest import UnitTest, deferred_function
from .test import TestRunner
from farmutils.error import send_exception_email


class TestController():
    def __init__(self, testrunner, setup_func=None, report_func=None,
            run_condition_func=None, name=None, report_n_iterations=None,
            continue_on_fail=True, run_forever=False, condition_check_interval_s=0,
            setup_every_iteration=False, force_initial_run=False, email_on_except=True,
            log_func=print):
        assert isinstance(testrunner, TestRunner)

        self.testrunner = testrunner
        self.setup = setup_func
        self.report = report_func
        self.run_condition = run_condition_func

        self.log_func = log_func or print

        self.name = name

        # Runtime settings
        self.settings = {}
        self.settings['run_forever'] = run_forever
        self.settings['report_n_iterations'] = report_n_iterations
        self.settings['continue_on_fail'] = continue_on_fail
        self.settings['condition_check_interval_s'] = condition_check_interval_s
        self.settings['setup_every_iteration'] = setup_every_iteration
        self.settings['force_initial_run'] = force_initial_run
        self.settings['email_on_except'] = email_on_except

        # Runtime statistics
        self.stats = {}
        self.stats['num_iterations_run'] = 0
        self.stats['num_iterations_pass'] = 0
        self.stats['num_iterations_fail'] = 0
        self.stats['num_tests_run'] = 0
        self.stats['num_tests_pass'] = 0
        self.stats['num_tests_fail'] = 0

        self.results = {}

        # Global data to be used by tests
        # Save TestController data here too
        self.data = {
            'TestController': {
                'settings': self.settings,
                'stats': self.stats,
                'results': self.results
            }
        }


    @property
    def setup(self):
        return self._setup

    @setup.setter
    def setup(self, f):
        self._setup = None if f is None else deferred_function(f)

    @property
    def report(self):
        return self._report

    @report.setter
    def report(self, f):
        self._report = None if f is None else deferred_function(f)

    @property
    def run_condition(self):
        return self._run_condition

    @run_condition.setter
    def run_condition(self, f):
        self._run_condition = None if f is None else deferred_function(f)

    def log(self, message):
        self.log_func('[{}] {}'.format(self.__class__.__name__, message))

    @property
    def iteration_results(self):
        try:
            ir = [r for r in self.results
                if r['iteration'] == self.stats['num_iterations_run']][0]
        except IndexError:
            ir = self._init_iteration_results()

        return ir

    #FIXME: Currently the same test object is used for each test iterration,
    #   meaning that it maintains state. This causes many unexpected issues!
    #   This needs to be fixed so that each iteraction gets a clean test object.
    def run_iteration(self):
        self.log("Starting iteration: {}".format(
            self.stats['num_iterations_run']))
        self.log("Current stats:\n\tIterations passed: {}/{} , Total tests passed: {}/{} ".format(
            self.stats['num_iterations_pass'], self.stats['num_iterations_run'],
            self.stats['num_tests_pass'], self.stats['num_tests_run']))

        if self.setup and self.settings['setup_every_iteration']:
            self.log("Running setup function: {}".format(self.setup))
            self.setup.run(self)

        self.log("Running TestRunner: {}".format(self.testrunner))
        self.iteration_results['success'] = self.testrunner.run()
        self.iteration_results['ran'] = True

        num_tests_pass = len([
            t for t in self.testrunner.data if not t['tasks']['failed']])
        num_tests_fail = self.testrunner.num_tests - num_tests_pass

        self.stats['num_tests_run'] += self.testrunner.num_tests
        self.stats['num_tests_pass'] += num_tests_pass
        self.stats['num_tests_fail'] += num_tests_fail

        self.stats['num_iterations_run'] += 1
        if self.iteration_results['success']:
            self.stats['num_iterations_pass'] += 1
            self.log("Test iteration complete: PASS".format(test))
        else:
            self.stats['num_iterations_fail'] += 1
            self.log("Test iteration complete: FAIL".format(test))

        return all_tests_pass

    def run(self):
        if self.settings['email_on_except']:
            try:
                self._run()
            # If exception is one we deliberately caused, don't handle it
            except KeyboardInterrupt as e:
                raise e
            except InterruptedError as e:
                raise e
            except Exception as e:
                send_exception_email(e)
                raise e
        else:
            self._run()

        self._finalise_iteration_results()

    def _run(self):
        self.stats['num_iterations_run'] = 0
        self.stats['num_iterations_pass'] = 0
        self.stats['num_iterations_fail'] = 0
        self.stats['num_tests_run'] = 0
        self.stats['num_tests_pass'] = 0
        self.stats['num_tests_fail'] = 0

        self.log("Starting TestController with settings: {}".format(
            self.settings))

        if self.setup and not self.settings['setup_every_iteration']:
            self.log("Running setup function: {}".format(self.setup))
            self.setup.run(self)

        while True:
            if self.run_condition:
                if (self.settings['force_initial_run'] and
                        self.stats['num_iterations_run'] == 0):
                    self.log("Ignoring run condition for first run")
                    run_now = True
                else:
                    self.log("Checking run condition function: {}".format(
                        self.run_condition))
                    run_now = self.run_condition.run(self)

                while run_now:
                    success = self.run_iteration()
                    if not success and not self.settings['continue_on_fail']:
                        if self.report:
                            self.log("Running report function: {}".format(self.report))
                            self.report.run(self)
                        return
                    if (self.settings['report_n_iterations'] and
                        self.stats['num_iterations_run'] % self.settings['report_n_iterations'] == 0):
                        if self.report:
                            self.log("Running report function: {}".format(self.report))
                            self.report.run(self)

                    self.log("Checking run condition function: {}".format(
                        self.run_condition))
                    run_now = self.run_condition.run(self)
            else:
                self.run_iteration()

            if self.report:
                self.log("Running report function: {}".format(self.report))
                self.report.run(self)

            if self.settings['run_forever']:
                if self.settings['condition_check_interval_s']:
                    self.log("Sleeping for {} seconds...".format(
                        self.settings['condition_check_interval_s']))
                    time.sleep(self.settings['condition_check_interval_s'])
            else:
                self.log("UnitTestSuite finished")
                return

    def _init_iteration_results(self):
        skeleton = {
            'iteration': self.settings['num_iterations_run']
            'start': datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
            'end': None,
            'success': None
            'TestRunner': self.testrunner.data
            }
        }
        self.results.append(skeleton)

        return self.results[-1]

    def _finalise_iteration_results(self):
        # Create copies of all TestRunner data
        self.iteration_results['TestRunner'] = deepcopy(self.testrunner.data)
        self.iteration_results['end'] = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')