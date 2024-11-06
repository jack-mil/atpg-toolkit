#!/usr/bin/env python3
import csv
import math
from pathlib import Path

import sys

# Import Path manipulation so script can live in a subfolder
this_dir = Path(__file__).parent
sys.path.append(str(this_dir.parent))

from simulator import FaultSimulation, util  # noqa: E402

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


def calc_coverage(target: float, tolerance: float, file: Path):
    sim = FaultSimulation(file)
    total_nets = sim.circuit.net_count()
    total_fault_count = 2 * total_nets

    input_length = sim.circuit.input_count()

    all_detected_faults = set()
    num_applied_tests = 0

    data: list[tuple[int, float]] = list()

    print(f'Testing circuit {file}')
    for new_test in util.random_patterns(input_length):
        detected_faults = sim.detect_faults(new_test)

        all_detected_faults.update(detected_faults)

        num_detected_faults = len(all_detected_faults)

        coverage = num_detected_faults / total_fault_count
        num_applied_tests += 1

        # save point (num_applied_tests, coverage (%))
        data.append((num_applied_tests, coverage))

        if num_applied_tests % 100 == 0:
            print(f'Tests: {num_applied_tests:04d} Coverage: {coverage:.05%}')

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
    data = calc_coverage(target, tolerance, file)

    with open(out_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows(data)
