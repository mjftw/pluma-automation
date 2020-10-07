import time
import json
from datetime import datetime
from copy import deepcopy

from pluma.utils import send_exception_email, datetime_to_timestamp, \
    regex_filter_list

from .unittest import deferred_function
from pluma.test import TestRunner

from .resultsplotter import DefaultResultsPlotter
from .resultsprocessor import DefaultResultsProcessor


class TestController():
    ''' Runs a TestRunner over multiple iterations and processes test data.

    The TestController is the top level test object, and takes a TestRunner
    to run each iteration.
    All data saved by tests run by the TestRunner on each iteration are saved
    to the "data" dict.
    This data is readily filtered, accessed and graphed using the
    :meth:`get_test_data` and :meth:`graph_test_results` functions.
    The TestController's behaviour is defined by the settings stored in the
    "settings" dict, which is populated with the arguments below.

    Example:
        >>> tc = TestController(my_testrunner)
        >>> tc.run()
        >>> my_data = tc.get_test_data(output_format='csv')
        >>> with open('mydata.csv', 'w') as f:
                f.write(my_data)
        >>> tc.graph_test_results('mygraph.svg')

    Args:
        testrunner: TestRunner object to be run each iteration.
            See :class:`~pluma.test.test.TestRunner`
        setup (deffered_function): Setup function.
            Default: None, no setup function.
            See :meth:`setup`
        report (deffered_function): Report function.
            Default: None, no report function.
            See :meth:`report`
        run_condition (deffered_function): Run condition function.
            Default: None, no run condition function.
            See :meth:`run_condition`
        name (str): Name of TestController. **DEPRECIATED**
        report_n_iterations (int): Run :meth:`report` function every N iterations.
            Saved to :attr:`settings`
            Default: None, only run at end of last test iteration.
        continue_on fail (bool): Continue running test iterations even if a
            test fails by raising an exception.
            Saved to :attr:`settings`
            Default: True
        run_forever (bool): Prevent TestController from exiting after a
            the :meth:`run_condition` function returns False.
            Saved to :attr:`settings`
            Default: False
        condition_check_interval_s (int): Number of seconds to wait before
            rechecking the :meth:`run_condition` function.
            Saved to :attr:`settings`
            Default: 0 seconds, retry immediately
        setup_n_iterations (int): Run setup function every N iterations.
            Default: None, only run :meth:`setup` the at start the of first iteration.
            Saved to :attr:`settings`
        force_initial_run (bool): Run an initial test iteration regardless of
            whether :meth:`run_condition` function returns True.
            Saved to :attr:`settings`
            Default: False
        email_on_except (bool): Send an error report email if an exception
            occurs during testing.
            Saved to :attr:`settings`
            Default: True
            See :func:`~pluma.utils.email.send_exception_email`
        log_func (function): Log function to use.
            Default: print
        results_plotter (:class:`~pluma.test.resultsplotter.ResultsPlotter`): Plotter to be used
            to graph test results.
            Defaults to :class:`~pluma.test.resultsplotter.DefaultResultsPlotter`
        results_processor (:class:`~pluma.test.resultsprocessor.ResultsProcessor`): Processor to
            be used to format test results.
            Defaults to :class:`~pluma.test.resultsprocessor.DefaultResultsProcessor`

    Attributes:
        settings (dict): Controls the behaviour of the TestController.
            Settings are populated from args above.
            Items:
                run_forever, report_n_iterations, continue_on_fail,
                condition_check_interval_s, setup_n_iterations, force_initial_run,
                email_on_except
        stats (dict): Contains TestController's runtime statistics.
            num_iterations_run: Total number of iterations run.
            num_iterations_pass: Number of iterations with no test failures.
            num_tests_run: Number of tests run over all iterations.
            num_tests_pass: Number of tests that succeded.
            num_tests_total: Total number of passed and failed tests.
        data (dict): Data dict containing data TestRunner runs and
            various other info.
            Initialised as:
                >>> self.data = {
                        'TestController': {
                            'settings': {},
                            'stats': {},
                            'results': {},
                            'results_summary': {},
                            'test_settings': {}
                        }
                    }
    '''

    def __init__(self, testrunner, setup=None, report=None,
                 run_condition=None, name=None, report_n_iterations=None,
                 continue_on_fail=True, run_forever=False, condition_check_interval_s=0,
                 setup_n_iterations=None, force_initial_run=False, email_on_except=True,
                 log_func=None, verbose_log_func=None, debug_log_func=None,
                 results_plotter=None, results_processor=None):
        assert isinstance(testrunner, TestRunner)

        self.testrunner = testrunner
        self.setup = setup
        self.report = report
        self.run_condition = run_condition

        self.log_func = log_func or print
        self.verbose_log_func = verbose_log_func
        self.debug_log_func = debug_log_func

        self.name = name

        self.results_plotter = results_plotter or DefaultResultsPlotter()
        self.results_processor = results_processor or DefaultResultsProcessor()

        # Global data to be used by tests
        # Save TestController data here too
        self.data = {
            'TestController': {
                'settings': {},
                'stats': {},
                'results': {},
                'results_summary': {},
                'test_settings': {}
            }
        }

        # Runtime settings
        self.settings = {}
        self.settings['run_forever'] = run_forever
        self.settings['report_n_iterations'] = report_n_iterations
        self.settings['continue_on_fail'] = continue_on_fail
        self.settings['condition_check_interval_s'] = condition_check_interval_s
        self.settings['setup_n_iterations'] = setup_n_iterations
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

    @property
    def settings(self):
        ''' The Testcontroller settings control control its behaviour. '''
        return self.data['TestController']['settings']

    @settings.setter
    def settings(self, settings):
        self.data['TestController']['settings'] = settings

    @property
    def stats(self):
        ''' Testcontroller runtime statistics '''
        return self.data['TestController']['stats']

    @stats.setter
    def stats(self, stats):
        self.data['TestController']['stats'] = stats

    @property
    def results(self):
        ''' Saved test runtime results.

        ll the data values saved to the "data" dicts of
        the tests in the TestRunner, over all iterations that have been run.
        '''
        return self.data['TestController']['results']

    @results.setter
    def results(self, results):
        self.data['TestController']['results'] = results

    @property
    def results_summary(self):
        ''' Summary of saved test results.

        A summary of all the data values saved to the "data" dicts of
        the tests in the TestRunner, over all iterations that have been run.
        '''
        return self.data['TestController']['results_summary']

    @results_summary.setter
    def results_summary(self, results_summary):
        self.data['TestController']['results_summary'] = results_summary

    @property
    def test_settings(self):
        ''' Dictionary summarising the test settings.

        A summary of all the settings saved to the "settings" dicts of
        the tests in the TestRunner.
        '''
        return self.data['TestController']['test_settings']

    @test_settings.setter
    def test_settings(self, test_settings):
        self.data['TestController']['test_settings'] = test_settings

    @property
    def setup(self):
        ''' Setup function, converted to a deffered_function if not already.

        If set, the setup function is run at the start of the first test
        iteration, and every N iterations if the "setup_every_n_iterations"
        setting is used.
        '''
        return self._setup

    @setup.setter
    def setup(self, f):
        self._setup = None if f is None else deferred_function(f)

    @property
    def report(self):
        ''' Report function, converted to a deffered_function if not already.

        If set, the setup function is run at the end of the last test
        iteration, and every N iterations if the "report_every_n_iterations"
        setting is used.
        '''
        return self._report

    @report.setter
    def report(self, f):
        self._report = None if f is None else deferred_function(f)

    @property
    def run_condition(self):
        ''' Run condition function, converted to a deffered_function if not already.

        If set, the run condition function is run before every test iteration, and
        it is used to determine whether another test iteration should be run.
        If if it returns True, another iteration is run, and False causes the
        TestController to exit.
        The TestController will not exit if the "run_forever" setting is set. If so
        the TestController will sleep for a number of seconds (as determined by the
        "condition_check_interval_s" setting) and the run condition function will
        be checked again. And so on.
        '''
        return self._run_condition

    @run_condition.setter
    def run_condition(self, f):
        self._run_condition = None if f is None else deferred_function(f)

    def log(self, message):
        ''' Basic logging function wrapper

        Calls the class method "log_func" (default is print) with a message.
            >>> my_testcontroller.log('Hello World!')
                'Hello World!'
        '''
        self.log_func(message)

    def verbose_log(self, message):
        ''' Logging function wrapper for verbose content '''
        if self.verbose_log_func:
            self.verbose_log_func(message)

    def debug_log(self, message):
        ''' Logging function wrapper for debug content '''
        if self.debug_log_func:
            self.debug_log_func(message)

    def get_test_data_summary(self):
        ''' Get a summary of test results data values, with some numerical analysis '''
        return self.results_processor.generate_summary(self.testrunner.tests, self.results)

    def collect_test_settings(self):
        ''' Get a summary of the settings for tests in the TestRunner '''
        settings = {}
        for test in self.testrunner.tests:
            if (not self.results or
                    str(test) not in self.results[0]['TestRunner']):
                # Test has not run, cannot get settings
                break
            if str(test) not in settings:
                # NOTE: Assuming test settings never change between iterations
                settings[str(test)] = self.results[0]['TestRunner'][str(
                    test)]['settings']

        return settings

    def get_test_data(self, test_names=None, fields=None, output_format=None,
                         settings=None):
        '''Get test data from the global data dictionary.

        Args:
            test_names (str, list(str)): The name of the test(s) to get data for.
                This can be a single test or a list of test names.
                These names are checked as regular expressions, with data from
                any test name matching any of the regex specified being returned.
                E.g.
                    >>> test_names=[MyTest.*, Test2]
                Default: match all test names.
                Tip: test_names='^(?!TestCore).*$' will filter out TestCore.
            fields (list(str)): A list of the names of data fields to extract.
                Default: all fields are returned.
            settings (dict): Optional. Specify a dict of
                key, value pairs, each representing the name and values of
                settings that must be present in the test's settings in order
                for it to be included in the returned results.
                E.g
                    >>> settings = {'mysetting1': 4, 'mysetting2': 'some_value'}
            output_format (str): Output format of returned data.
                Can be set to the following:
                    'json' -> return data is a json formatted string
                    'csv' -> return data is CSV formatted
                    Default: return data is a generator to create a list of dicts
                    E.g.
                        >>> field1_data = list(returned)[iteration_number]['test_name']['field1']
        '''

        test_names = test_names or '.*'
        if not isinstance(test_names, list):
            test_names = [test_names]

        # Add a $ to the end of every regex to make it less greedy
        test_names = [f'{t}$' for t in test_names]

        def data_gen():
            for r in (result['TestRunner'] for result in self.results):
                yield {
                    name: {
                        f: v for f, v in r[name]['data'].items() if 'data' in r[name] and
                        not fields or f in fields
                    } for name in regex_filter_list(test_names, r, unique=True)
                    if not settings or
                    all(key in r[name]['settings'] and
                        r[name]['settings'][key] == val
                        for key, val in settings.items())
                }

        if output_format == 'json':
            return json.dumps(list(data_gen()), indent=4)
        elif output_format == 'csv':
            newline = '\n'
            header = sorted(list(set(key for it_data in data_gen()
                                     for test, data in it_data.items() for key in data)))
            csv_str = 'iteration,test_name,' + \
                ','.join(header).replace('\n', ' ').replace('\r', '') + newline
            empty_csv = True
            for iteration, tests_data in enumerate(data_gen()):
                for test_name, data in tests_data.items():
                    empty_csv = False
                    csv_str += f'{iteration},{test_name}'
                    for h in header:
                        csv_str += ','
                        if h in data:
                            csv_str += str(data[h]).replace('\n',
                                                            ' ').replace('\r', '')
                    csv_str += newline
            return csv_str if not empty_csv else ''
        elif not output_format:
            return data_gen()
        else:
            raise RuntimeError(
                f'Invalid format: {output_format}. Options: "json", "csv", None')

    def graph_test_results(self, file, test_names=None, fields=None, vs_type=None,
                           title=None, output_format=None, config=None):
        '''Create a graph of data fields from the test results data'''
        results = list(self.get_test_data(test_names=test_names, fields=fields))
        self.results_plotter.plot(file, results=results, test_names=test_names, fields=fields,
                                  vs_type=vs_type, title=title, output_format=output_format, config=config)

    def run_iteration(self):
        ''' Run all tests in TestRunner '''
        iteration = self.stats['num_iterations_run']
        if iteration > 0:
            self.log(f'Starting iteration #{iteration+1}')
            self.log('Current stats:\n\tIterations passed/total: {}/{},'
                     ' Tests pass/run/total: {}/{}/{} '.format(
                         self.stats['num_iterations_pass'], iteration,
                         self.stats['num_tests_pass'], self.stats['num_tests_run'],
                         self.stats['num_tests_total']))

        self._init_iteration()

        self.debug_log(f'Running TestRunner: {self.testrunner}')
        success = self.testrunner.run()

        self._finalise_iteration(success)

        if success:
            self.log("Test iteration complete: PASS")
        else:
            self.log("Test iteration complete: FAIL")

        return success

    def run(self):
        ''' Run the test suite with saved settings '''
        try:
            return self._run()
        # If exception is one we deliberately caused, don't handle it
        except KeyboardInterrupt as e:
            raise e
        except InterruptedError as e:
            raise e
        except Exception as e:
            if self.settings['email_on_except']:
                send_exception_email(e)
            raise e

    def _run(self):
        self.stats['num_iterations_run'] = 0
        self.stats['num_iterations_pass'] = 0
        self.stats['num_tests_run'] = 0
        self.stats['num_tests_pass'] = 0
        self.stats['num_tests_total'] = 0

        self.debug_log(f'Starting TestController with settings: {self.settings}')
        self.debug_log(f'Test settings: {self.test_settings}')

        if self.setup and not self.settings['setup_n_iterations']:
            self.debug_log(f"Running setup function: {self.setup}")
            self.setup.run(self)

        success = True

        while True:
            if self.run_condition:
                if (self.settings['force_initial_run'] and
                        self.stats['num_iterations_run'] == 0):
                    self.debug_log('Ignoring run condition for first run')
                    run_now = True
                else:
                    self.debug_log(f'Checking run condition function: {self.run_condition}')
                    run_now = self.run_condition.run(self)

                while run_now:
                    num_iterations = self.stats['num_iterations_run']

                    if (self.settings['setup_n_iterations'] and
                            num_iterations % self.settings['setup_n_iterations'] == 0):
                        if self.setup:
                            self.debug_log(f'Running setup function: {self.setup}')
                            self.setup.run(self)
                    success &= self.run_iteration()
                    if not success and not self.settings['continue_on_fail']:
                        if self.report:
                            self.debug_log(f'Running report function: {self.report}')
                            self.report.run(self)
                        return False
                    if (self.settings['report_n_iterations'] and
                            num_iterations % self.settings['report_n_iterations'] == 0):
                        if self.report:
                            self.debug_log(f'Running report function: {self.report}')
                            self.report.run(self)

                    self.debug_log(f'Checking run condition function: {self.run_condition}')
                    run_now = self.run_condition.run(self)
            else:
                self.run_iteration()

            if self.report and not self.settings['report_n_iterations']:
                self.verbose_log(f'Running report function: {self.report}')
                self.report.run(self)

            if self.settings['run_forever']:
                check_interval = self.settings['condition_check_interval_s']
                if check_interval:
                    self.log(f'Sleeping for {check_interval} seconds...')
                    time.sleep(check_interval)
            else:
                return success

    def _init_iteration(self):
        skeleton = {
            'iteration': self.stats['num_iterations_run'],
            'start': datetime_to_timestamp(datetime.now()),
            'end': None,
            'success': None,
            'test_order': None,
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
        if self.testrunner.sequential:
            self.results[-1]['test_order'] = 'sequential'
        else:
            self.results[-1]['test_order'] = 'parallel'

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

        self.results_summary = self.get_test_data_summary()
        self.test_settings = self.collect_test_settings()
