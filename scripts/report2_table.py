#!/usr/bin/env python3
"""Script for the data to include in report 2 for project part 2."""

import sys
from pathlib import Path

# Import Path manipulation so script can live in a subfolder
this_dir = Path(__file__).parent
sys.path.append(str(this_dir.parent))

from simulator import FaultSimulation  # noqa: E402

test_cases = [
    # (netlist file, input vector)
    ('circuits/s27.net', '1101101'),
    ('circuits/s27.net', '0101001'),
    ('circuits/s298f_2.net', '10101011110010101'),
    ('circuits/s298f_2.net', '11101110101110111'),
    ('circuits/s344f_2.net', '101010101010111101111111'),
    ('circuits/s344f_2.net', '111010111010101010001100'),
    ('circuits/s349f_2.net', '101000000010101011111111'),
    ('circuits/s349f_2.net', '111111101010101010001111'),
]

for file, test in test_cases:
    path = Path(file)
    sim = FaultSimulation(path)
    faults = sim.detect_faults(test)
    # output in format for typst table
    # print(f'[{file.name}], [{test}], [{len(faults)}],')

    print(f'=== Circuit: {path.stem}')
    print(f'- Input Vector: `{" ".join(test)}`')
    print(f'- Detected Faults: {len(faults)}')
    print(f'#figure(caption:[{path.stem} (`{"".join(test)}`)],')
    print('table(columns:9,')
    for f in sorted(faults):
        print(f'[{f.net_id} s-a-{f.stuck_at}],')
    print('))')
    print()
    print(flush=True)
