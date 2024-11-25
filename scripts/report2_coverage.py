#!/usr/bin/env python3

# A quick and dirty script used for generating coverage data to plot in report 2
# Only intended to run once, and as such is not in a completely working state
# I modified the script to generate data as I needed it for Excel plots and the report tables
#
# This does serve as a good reference of the public simulator API in action

import csv
import math
import sys
from itertools import zip_longest
from pathlib import Path

# Import Path manipulation so script can live in a subfolder
this_dir = Path(__file__).parent
sys.path.append(str(this_dir.parent))

from atpg_toolkit import FaultSimulation, util  # noqa: E402

target = 1.0  # 100% coverage
tolerance = 5e-3  # within 0.5%

files = map(
    this_dir.parent.joinpath,
    [
        'circuits/s27.net',
        'circuits/s298f_2.net',
        'circuits/s344f_2.net',
        'circuits/s349f_2.net',
    ],
)


def calc_coverage(target: float, tolerance: float, sim: FaultSimulation):
    total_nets = sim.circuit.net_count()
    total_fault_count = 2 * total_nets
    input_length = sim.circuit.input_count()

    all_detected_faults = set()
    num_applied_tests = 0

    data: list[tuple[int, float]] = list()

    for new_test in util.random_patterns(input_length):
        detected_faults = sim.detect_faults(new_test)

        all_detected_faults.update(detected_faults)

        num_detected_faults = len(all_detected_faults)

        coverage = num_detected_faults / total_fault_count
        num_applied_tests += 1

        # save point (num_applied_tests, coverage (%))
        data.append((num_applied_tests, coverage))

        if math.isclose(coverage, target, rel_tol=tolerance):
            # quit when target reached
            break

        if num_applied_tests > 1000:
            # also quit if we are making no progress
            break

    return data


for file in files:
    name = file.stem
    out_file = file.parent.parent / 'data' / f'{name}-coverage.csv'

    sim = FaultSimulation(file)

    perc_75_avg = 0
    perc_90_avg = 0

    iterations = 15

    # all_data = []
    for _ in range(iterations):
        data = calc_coverage(target, tolerance, sim)

        # all_data.append(data)

        perc_75 = next(num for num, coverage in data if coverage > 0.75)
        perc_90 = next(num for num, coverage in data if coverage > 0.9)

        perc_75_avg += perc_75 / iterations
        perc_90_avg += perc_90 / iterations

    # output in format for typst table
    print(f'[{file.name}], [{sim.circuit.net_count()}], [{perc_75_avg:.1f}], [{perc_90_avg:.1f}],')

    # columns = zip_longest(*all_data, fillvalue=1)

    # with open(out_file, 'w', newline='') as csvfile:
    #     writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
    #     writer.writerows(data)
