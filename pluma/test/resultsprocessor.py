from abc import ABC, abstractmethod
from typing import List
from pluma.test.testbase import TestBase

from statistics import mean, median_grouped, mode, stdev, variance,\
    StatisticsError


class ResultsProcessor(ABC):
    @abstractmethod
    def generate_summary(self, tests: list, results: list) -> dict:
        '''Generate a summary of the test results passed in.'''


class DefaultResultsProcessor(ResultsProcessor):
    def generate_summary(self, tests: List[TestBase], results: list) -> dict:
        """Get a summary of test results data values, with some numerical analysis"""
        def chunks(results_list, n):
            """Yield successive n-sized chunks from results_list"""
            for i in range(0, len(results_list), n):
                yield results_list[i:i + n]

        def chunked_mean(results_list, n, sigfig=2):
            """Chunk the list results_list into n equal chunks, and calculate the mean of
            each chunk. If n > length of results_list, then the length of results_list is
            used instead. This gives the mean for first x values, then next x values etc."""
            chunked_list = chunks(results_list, min(
                round(len(results_list)/n) or 1, len(results_list)))
            chunked_mean_list = list(map(
                lambda x: round(mean(x), sigfig),
                chunked_list
            ))
            if len(chunked_mean_list) > n:
                chunked_mean_list = chunked_mean_list[0: n]
            return chunked_mean_list

        results_summary = {}
        for test in (t for t in tests if t.data):
            testname = str(test)
            # Collect data
            if testname not in results_summary:
                results_summary[testname] = {}

            for iteration, _ in enumerate(results):
                for data_key in results[iteration]['TestRunner'][testname]['data']:
                    if data_key not in results_summary[testname]:
                        results_summary[testname][data_key] = {}
                    data_value = results[iteration]['TestRunner'][testname]['data'][data_key]

                    # Collect values in list
                    if 'values' not in results_summary[testname][data_key]:
                        results_summary[testname][data_key]['values'] = []
                    results_summary[testname][data_key]['values'].append(
                        data_value)

                    # Count of data value
                    if 'count' not in results_summary[testname][data_key]:
                        results_summary[testname][data_key]['count'] = {}
                    if str(data_value) not in results_summary[testname][data_key]['count']:
                        results_summary[testname][data_key]['count'][str(
                            data_value)] = 0
                    results_summary[testname][data_key]['count'][str(
                        data_value)] += 1

            # Calculate statistical data
            for data_key in results_summary[testname]:
                n_values = len(results_summary[testname][data_key]['values'])
                # Can't generate statistics from a single data point
                if n_values >= 2:
                    # Statistics calculated for numbers only
                    if all((isinstance(d, int) or isinstance(d, float))
                            and not isinstance(d, bool)
                            for d in results_summary[testname][data_key]['values']):
                        results_summary[testname][data_key]['max'] = max(
                            results_summary[testname][data_key]['values'])

                        results_summary[testname][data_key]['min'] = min(
                            results_summary[testname][data_key]['values'])

                        try:
                            results_summary[testname][data_key]['mode'] = mode(
                                results_summary[testname][data_key]['values'])
                        except StatisticsError:
                            # This happens when there is no unique mode
                            results_summary[testname][data_key]['mode'] = None

                        results_summary[testname][data_key]['mean'] = round(mean(
                            results_summary[testname][data_key]['values']), 2)

                        results_summary[testname][data_key]['median'] = round(median_grouped(
                            results_summary[testname][data_key]['values']), 2)

                        results_summary[testname][data_key]['stdev'] = round(stdev(
                            results_summary[testname][data_key]['values']), 2)

                        results_summary[testname][data_key]['variance'] = round(variance(
                            results_summary[testname][data_key]['values']), 2)

                    # Statistics calculated for numbers or booleans
                    if all(isinstance(d, int) or isinstance(d, float)
                            or isinstance(d, bool)
                            for d in results_summary[testname][data_key]['values']):
                        # Chunk the data into equal chunks, and calculate the chunks mean
                        # This gives the mean for first x values, then next x values etc.
                        # Number of chunks is lowest of 10 and the length of the dataset
                        results_summary[testname][data_key]['chunked_mean'] = chunked_mean(
                            results_summary[testname][data_key]['values'], 10)
                # We do not want all the data duplicated in the summary
                del(results_summary[testname][data_key]['values'])

        return results_summary
