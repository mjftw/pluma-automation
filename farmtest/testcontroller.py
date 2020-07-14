import time
import json
import re
import pygal
from datetime import datetime
from copy import deepcopy
from statistics import mean, median_grouped, mode, stdev, variance,\
    StatisticsError

from farmutils import send_exception_email, datetime_to_timestamp, \
    regex_filter_list

from .unittest import deferred_function
from .test import TestRunner


class TestController():
    ''' Runs a TestRunner over multiple iterations and processes test data.

    The TestController is the top level test object, and takes a TestRunner
    to run each iteration.
    All data saved by tests run by the TestRunner on each iteration are saved
    to the "data" dict.
    This data is readily filtered, accessed and graphed using the
    :meth:`get_test_results` and :meth:`graph_test_results` functions.
    The TestController's behaviour is defined by the settings stored in the
    "settings" dict, which is populated with the arguments below.

    Example:
        >>> tc = TestController(my_testrunner)
        >>> tc.run()
        >>> my_data = tc.get_test_results(format='csv')
        >>> with open('mydata.csv', 'w') as f:
                f.write(my_data)
        >>> tc.graph_test_results('mygraph.svg')

    Args:
        testrunner: TestRunner object to be run each iteration.
            See :class:`~farmtest.test.TestRunner`
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
            See :func:`~farmutils.email.send_exception_email`
        log_func (function): Log function to use.
            Default: print

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
            log_func=print):
        assert isinstance(testrunner, TestRunner)

        self.testrunner = testrunner
        self.setup = setup
        self.report = report
        self.run_condition = run_condition

        self.log_func = log_func or print

        self.name = name

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
        ''' Basic logging function wraper

        Calls the class method "log_func" (default is print) with a message.
            >>> my_testcontroller.log('Hello World!')
                '[TestController] Hello World!'
        '''
        self.log_func('[{}] {}'.format(self.__class__.__name__, message))

    def get_results_summary(self):
        ''' Get a summary of test results data values,
            with some numerical analysis '''
        def chunks(l, n):
            '''Yield successive n-sized chunks from l'''
            for i in range(0, len(l), n):
                yield l[i:i + n]

        def chunked_mean(l, n, sigfig=2):
            '''Chunk the list l into n equal chunks, and calculate the mean of
            each chunk. If n > length of l, then the length of l is used instead.
            This gives the mean for first x values, then next x values etc.'''
            chunked_list = chunks(l, min(round(len(l)/n) or 1, len(l)))
            chunked_mean_list =  list(map(
                lambda x: round(mean(x), sigfig),
                chunked_list
            ))
            if len(chunked_mean_list) > n:
                chunked_mean_list = chunked_mean_list[0: n]
            return chunked_mean_list

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
                n_values = len(results_summary[test][data_key]['values'])
                # Can't generate statistics from a single data point
                if n_values >= 2:
                    # Statistics calculated for numbers only
                    if all((isinstance(d, int) or isinstance(d, float))
                            and not isinstance(d, bool)
                            for d in results_summary[test][data_key]['values']):
                        results_summary[test][data_key]['max'] = max(
                            results_summary[test][data_key]['values'])

                        results_summary[test][data_key]['min'] = min(
                            results_summary[test][data_key]['values'])

                        try:
                            results_summary[test][data_key]['mode'] = mode(
                                results_summary[test][data_key]['values'])
                        except StatisticsError:
                            # This happens when there is no unique mode
                            results_summary[test][data_key]['mode'] = None

                        results_summary[test][data_key]['mean'] = round(mean(
                            results_summary[test][data_key]['values']), 2)

                        results_summary[test][data_key]['median'] = round(median_grouped(
                            results_summary[test][data_key]['values']), 2)

                        results_summary[test][data_key]['stdev'] = round(stdev(
                            results_summary[test][data_key]['values']), 2)

                        results_summary[test][data_key]['variance'] = round(variance(
                            results_summary[test][data_key]['values']), 2)

                    # Statistics calculated for numbers or booleans
                    if all(isinstance(d, int) or isinstance(d, float)
                            or isinstance(d, bool)
                            for d in results_summary[test][data_key]['values']):
                        # Chunk the data into equal chunks, and calculate the chunks mean
                        # This gives the mean for first x values, then next x values etc.
                        # Number of chunks is lowest of 10 and the length of the dataset
                        results_summary[test][data_key]['chunked_mean'] = chunked_mean(
                            results_summary[test][data_key]['values'], 10)
                # We do not want all the data duplicated in the summary
                del(results_summary[test][data_key]['values'])

        return results_summary

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
                settings[str(test)] = self.results[0]['TestRunner'][str(test)]['settings']

        return settings

    def get_test_results(self, test_names=None, fields=None, format=None,
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
            format (str): Output format of returned data.
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

        if format == 'json':
            return json.dumps(list(data_gen()), indent=4)
        elif format == 'csv':
            newline = '\n'
            header = sorted(list(set(key for it_data in data_gen() for test, data in it_data.items() for key in data)))
            csv_str = 'iteration,test_name,' + ','.join(header).replace('\n', ' ').replace('\r', '') + newline
            empty_csv = True
            for iteration, tests_data in enumerate(data_gen()):
                for test_name, data in tests_data.items():
                    empty_csv = False
                    csv_str += f'{iteration},{test_name}'
                    for h in header:
                        csv_str += ','
                        if h in data:
                            csv_str += str(data[h]).replace('\n', ' ').replace('\r', '')
                    csv_str += newline
            return csv_str if not empty_csv else ''
        elif not format:
            return data_gen()
        else:
            raise RuntimeError(
                f'Invalid format: {format}. Options: "json", "csv", None')

    def graph_test_results(self, file, test_names=None, fields=None, vs_type=None,
            title=None, format=None, config=None):
        '''Create a graph of data fields from the test results data.

        Args:
            file (str): Output file path.
            test_names (str, list(str)): Name of Tests to read data from.
                Can specify a one test name or a list of test names.
                All tests are selected if set to None.
            fields (str, list(str): List of data fields to plot from Test data.
                Default: all fields are plotted.
            vs_type (str): Specifies what should be on graph axis:
                "iteration": graph data values over test iterations.
                "fields": Graph the fields in fields argument with one on each axis.
                    If this option is selected, fileds must be exactly 2 fields.
                Default: "iteration"
            title (str): Optionally a title can be supplied for the chart.
                If a tile is not specified, one will be generated according to
                the test data.
            format (str): Specifies output format.
                Options: "svg" or "png"
                Default: "svg"
            config (pygal.Config): Optionally supply a option.
                This allows rendering with custom configuration and styles.
        '''

        vs_type = vs_type or 'iteration'
        format = format or 'svg'

        if fields and not isinstance(fields, list):
            fields = [fields]

        if test_names and not isinstance(test_names, list):
            test_names = [test_names]

        vs_types = ['iteration', 'cumulative', 'fields']
        if vs_type not in vs_types:
            raise AttributeError('vs_type must be in {}'.format(vs_types))
        elif (vs_type == 'fields' and
                (not isinstance(fields, list) or len(fields) != 2)):
            raise AttributeError(
                'fields must be a list of exactly 2 fields for "fields" vs_type')
        formats = ['svg', 'png']
        if format not in formats:
            raise AttributeError('Format must be one of {}'.format(formats))

        results = list(self.get_test_results(
            test_names=test_names, fields=fields))

        # Find any tests that do not have any data for fields specified
        empty_tests = set([test for r in results for test, data in r.items() if not data])

        if results:
            # Get a list of test names whose tests have data
            tests_found = sorted(list(set(test for r in results for test in r if test not in empty_tests)))
        else:
            tests_found = []

        if tests_found:
            # Get a list of all fields accross all test data found
            fields_found = list(set(key for r in results for test, data in r.items() for key in data))
        else:
            fields_found = []

        # If no results match, or all test names missing from from first result
        if not fields_found:
            raise RuntimeError(
                'No results found for test{}{}, fields{}'.format(
                    's' if len(tests_found) > 1 else '',
                    test_names,
                    fields))

        chart = pygal.XY(truncate_legend=-1)
        chart.title = title

        # Default style to fix svg black background rendering issue
        chart.config.style = pygal.style.Style(
            background='#FFFFFF',
            plot_background='#FFFFFF'
        )

        if config:
            if not isinstance(config, pygal.Config):
                raise AttributeError('config must be of type pygal.Config')
            chart.config = config

        points = {}

        if vs_type in ['iteration', 'cumulative']:
            vs_str = '{}{} vs iteration'.format(
                'cumulative ' if vs_type == 'cumulative' else '',
                ', '.join(fields_found))

            # Build list of points with dataset labels
            for tf in tests_found:
                points[tf] = {f'{tf}: {k}': [] for k in results[0][tf]}
                last_v = 0
                for i, r in enumerate(results):
                    # Filter out None results as these are not numbers and will break graphing.
                    for k, v in ((k, v) for k, v in r[tf].items() if v is not None):
                        if isinstance(v, bool):
                            v = int(v)
                        if vs_type == 'cumulative':
                            v += last_v
                            last_v = v

                        points[tf][f'{tf}: {k}'].append((i, v))

        elif vs_type == 'fields':
            tests_with_fields = [
                tf for tf in tests_found for r in results
                if fields[0] in r[tf] and fields[1] in r[tf]
            ]
            vs_str = '{} vs {}'.format(
                fields[0], fields[1])

            for tf in tests_with_fields:
                points[tf] = {
                    tf: [(r[tf][fields[0]], r[tf][fields[1]]) for r in results]}

        chart.title = chart.title or '{} for{} {}'.format(
            vs_str,
            ' tests:' if len(tests_found) > 1 else '',
            ', '.join(tests_found))

        if not points:
            raise RuntimeError(
                'No results found for test{}{}, fields{}'.format(
                    's' if len(tests_found) > 1 else '',
                    test_names,
                    fields))

        # Combine points for each test into one set
        points_combined = {}
        for _, points_v in points.items():
            for k, v in points_v.items():
                points_combined[k] = v

        # Add points to chart
        for k, v in points_combined.items():
            chart.add(k, v)

        if format == 'svg':
            chart.render_to_file(file)
        elif format == 'png':
            chart.render_to_png(file)

    def run_iteration(self):
        ''' Run all tests in TestRunner '''
        self.log("Starting iteration: {}".format(
            self.stats['num_iterations_run']))
        self.log("Current stats:\n\tIterations passed/total: {}/{} , Tests pass/run/total: {}/{}/{} ".format(
            self.stats['num_iterations_pass'], self.stats['num_iterations_run'],
            self.stats['num_tests_pass'], self.stats['num_tests_run'],
            self.stats['num_tests_total']))

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

        self.log("Starting TestController with settings: {}".format(
            self.settings))

        self.log("Test settings: {}".format(
            self.test_settings))

        if self.setup and not self.settings['setup_n_iterations']:
            self.log("Running setup function: {}".format(self.setup))
            self.setup.run(self)

        success = True

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
                    if (self.settings['setup_n_iterations'] and
                            self.stats['num_iterations_run'] % self.settings['setup_n_iterations'] == 0):
                        if self.setup:
                            self.log("Running setup function: {}".format(self.setup))
                            self.setup.run(self)
                    success &= self.run_iteration()
                    if not success and not self.settings['continue_on_fail']:
                        if self.report:
                            self.log("Running report function: {}".format(self.report))
                            self.report.run(self)
                        return False
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

            if self.report and not self.settings['report_n_iterations']:
                self.log("Running report function: {}".format(self.report))
                self.report.run(self)

            if self.settings['run_forever']:
                if self.settings['condition_check_interval_s']:
                    self.log("Sleeping for {} seconds...".format(
                        self.settings['condition_check_interval_s']))
                    time.sleep(self.settings['condition_check_interval_s'])
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

        self.results_summary = self.get_results_summary()
        self.test_settings = self.collect_test_settings()
