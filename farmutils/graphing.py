import pandas
import pygal
import math
import json


def boot_graph(data_file, output_file, boot_test_name,
               window=1, interpolate=None):
    with open(data_file, 'r') as f:
        all_data = json.load(f)

    boot_data = all_data[boot_test_name]
    boot_success_data = [d['boot_success'] for d in boot_data]

    series = pandas.Series(boot_success_data)
    mean_success = series.rolling(window=window).mean().to_list()
    mean_success_reduced = [m for m in mean_success if not math.isnan(m)]

    data_start_index = len(mean_success)-len(mean_success_reduced)

    line_chart = pygal.Line(interpolate=interpolate)
    line_chart.x_labels = list(range(data_start_index, len(mean_success_reduced)+1))
    line_chart.add(
        'Boot success with window {window} rolling mean', mean_success_reduced)
    line_chart.render_to_file(output_file)
