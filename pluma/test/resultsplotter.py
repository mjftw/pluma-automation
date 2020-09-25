from abc import ABC, abstractmethod
import pygal


class ResultsPlotter(ABC):
    @abstractmethod
    def plot(self, file, results: list, test_names=None, fields=None, vs_type=None,
             title=None, output_format=None, config=None):
        pass


class DefaultResultsPlotter(ResultsPlotter):
    def plot(self, file, results: list, test_names=None, fields=None, vs_type=None,
             title=None, output_format=None, config=None):
        """Create a graph of data fields from the test results data.
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
            output_format (str): Specifies output format.
                Options: "svg" or "png"
                Default: "svg"
            config (pygal.Config): Optionally supply a option.
                This allows rendering with custom configuration and styles.
        """
        vs_type = vs_type or 'iteration'
        output_format = output_format or 'svg'

        if fields and not isinstance(fields, list):
            fields = [fields]

        if test_names and not isinstance(test_names, list):
            test_names = [test_names]

        vs_types = ['iteration', 'cumulative', 'fields']
        if vs_type not in vs_types:
            raise AttributeError(f'vs_type must be in {vs_types}')
        elif (vs_type == 'fields' and
                (not isinstance(fields, list) or len(fields) != 2)):
            raise AttributeError(
                'fields must be a list of exactly 2 fields for "fields" vs_type')
        formats = ['svg', 'png']
        if output_format not in formats:
            raise AttributeError(f'Format must be one of {formats}')

        # Find any tests that do not have any data for fields specified
        empty_tests = set([test for r in results for test,
                           data in r.items() if not data])

        if results:
            # Get a list of test names whose tests have data
            tests_found = sorted(
                list(set(test for r in results for test in r if test not in empty_tests)))
        else:
            tests_found = []

        if tests_found:
            # Get a list of all fields accross all test data found
            fields_found = list(
                set(key for r in results for test, data in r.items() for key in data))
        else:
            fields_found = []

        # If no results match, or all test names missing from from first result
        if not fields_found:
            plural_or_not = 's' if len(tests_found) > 1 else ''
            raise RuntimeError(
                f'No results found for test{plural_or_not}{test_names}, fields{fields}')

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
            vs_str = f'{fields[0]} vs {fields[1]}'

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

        if output_format == 'svg':
            chart.render_to_file(file)
        elif output_format == 'png':
            chart.render_to_png(file)
