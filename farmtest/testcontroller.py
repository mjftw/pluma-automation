import time
import json
from datetime import datetime
from copy import deepcopy
from statistics import mean, median_grouped, mode, stdev, variance

from farmutils import send_exception_email, datetime_to_timestamp

from .unittest import UnitTest, deferred_function
from .test import TestRunner


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

        # Global data to be used by tests
        # Save TestController data here too
        self.data = {
            'TestController': {
                'settings': {},
                'stats': {},
                'results': {}
            }
        }

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
        self.stats['num_tests_run'] = 0
        self.stats['num_tests_pass'] = 0
        self.stats['num_tests_total'] = 0

        self.results = []

        self.data['results_summary'] = self.results_summary


    @property
    def settings(self):
        return self.data['TestController']['settings']

    @settings.setter
    def settings(self, settings):
        self.data['TestController']['settings'] = settings

    @property
    def stats(self):
        return self.data['TestController']['stats']

    @stats.setter
    def stats(self, stats):
        self.data['TestController']['stats'] = stats

    @property
    def results(self):
        return self.data['TestController']['results']

    @results.setter
    def results(self, results):
        self.data['TestController']['results'] = results

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
    def results_summary(self):
        results_summary = {}
        for test in [str(t) for t in self.testrunner.tests]:
            # Collect data
            if test not in results_summary:
                results_summary[test] = {}

            for iteration, result in enumerate(self.results):
                for data_key in self.results[iteration]['TestRunner'][test]['data']:
                    if data_key not in results_summary[test]:
                        results_summary[test][data_key] = {}
                    data_value = self.results[iteration]['TestRunner'][test]['data'][data_key]

                    # Collect values in list
                    if 'values' not in results_summary[test][data_key]:
                        results_summary[test][data_key]['values'] = []
                    results_summary[test][data_key]['values'].append(
                        data_value)

                    # Count of data value
                    if 'count' not in results_summary[test][data_key]:
                        results_summary[test][data_key]['count'] = {}
                    if str(data_value) not in results_summary[test][data_key]['count']:
                        results_summary[test][data_key]['count'][str(data_value)] = 0
                    results_summary[test][data_key]['count'][str(data_value)] += 1

            # Calculate statistical data
            for data_key in results_summary[test]:
                if isinstance(data_value, int) or isinstance(data_value, float):
                    results_summary[test][data_key]['max'] = max(
                        results_summary[test][data_key]['values'])

                    results_summary[test][data_key]['min'] = min(
                        results_summary[test][data_key]['values'])

                    results_summary[test][data_key]['mode'] = mode(
                        results_summary[test][data_key]['values'])

                    results_summary[test][data_key]['mean'] = round(mean(
                        results_summary[test][data_key]['values']), 2)

                    results_summary[test][data_key]['median'] = round(median_grouped(
                        results_summary[test][data_key]['values']), 2)

                    results_summary[test][data_key]['stdev'] = round(stdev(
                        results_summary[test][data_key]['values']), 2)

                    results_summary[test][data_key]['variance'] = round(variance(
                        results_summary[test][data_key]['values']), 2)

                # We do not want all the data duplicated in the summary
                del(results_summary[test][data_key]['values'])

        return results_summary

    def run_iteration(self):
        self.log("Starting iteration: {}".format(
            self.stats['num_iterations_run']))
        self.log("Current stats:\n\tIterations passed/total: {}/{} , Tests pass/run/total: {}/{}/{} ".format(
            self.stats['num_iterations_pass'], self.stats['num_iterations_run'],
            self.stats['num_tests_pass'], self.stats['num_tests_run'],
            self.stats['num_tests_total']))

        if self.setup and self.settings['setup_every_iteration']:
            self.log("Running setup function: {}".format(self.setup))
            self.setup.run(self)

        self._init_iteration()

        self.log("Running TestRunner: {}".format(self.testrunner))
        success = self.testrunner.run()

        self._finalise_iteration(success)

        if success:
            self.log("Test iteration complete: PASS")
        else:
            self.log("Test iteration complete: FAIL")

        return success

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

    def _run(self):
        self.stats['num_iterations_run'] = 0
        self.stats['num_iterations_pass'] = 0
        self.stats['num_tests_run'] = 0
        self.stats['num_tests_pass'] = 0
        self.stats['num_tests_total'] = 0

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
                self.log("==== TestController Results ====")
                self.log(self.results)
                return

    def _init_iteration(self):
        skeleton = {
            'iteration': self.stats['num_iterations_run'],
            'start': datetime_to_timestamp(datetime.now()),
            'end': None,
            'success': None,
            'TestRunner': self.testrunner.data
            }
        self.results.append(skeleton)

        return self.results[-1]

    def _finalise_iteration(self, success):
        # Create copies of all TestRunner data
        self.results[-1]['TestRunner'] = deepcopy(self.testrunner.data)

        # Update stats
        self.results[-1]['end'] = datetime_to_timestamp(datetime.now())
        self.results[-1]['success'] = success
        self.results[-1]['ran'] = True

        num_tests_run = len([
            k for k, v in self.testrunner.data.items()
            if v['tasks']['ran']])
        num_tests_pass = len([
            k for k, v in self.testrunner.data.items()
            if v['tasks']['ran'] and not v['tasks']['failed']])

        if success:
            self.stats['num_iterations_pass'] += 1

        self.stats['num_tests_run'] += num_tests_run
        self.stats['num_tests_pass'] += num_tests_pass
        self.stats['num_tests_total'] += self.testrunner.num_tests

        self.stats['num_iterations_run'] += 1
