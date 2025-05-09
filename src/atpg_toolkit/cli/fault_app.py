# SPDX-FileCopyrightText: 2024 jack-mil
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

from argparse import ArgumentParser

from atpg_toolkit.cli._helpers import add_action, extend_from_file, valid_path
from atpg_toolkit.faultsim import FaultSimulation

# Subcommand 'faults'
faults_cmd = ArgumentParser(
    description='Find detected faults with a given net-list and test vector(s)',
)
faults_cmd.add_argument(
    'net_file',
    type=valid_path,
    help='Net-list file (circuit) to detect faults on',
)
faults_cmd.add_argument(
    '-f',
    '--file',
    required=False,
    type=valid_path,
    help='path to a file containing additional test vector strings',
)
faults_cmd.add_argument(
    'input_vectors',
    nargs='*',
    help='One or more test vectors to apply to the circuit',
)


@add_action(faults_cmd)
def deduce(net_file: Path, input_vectors: list[str], file: Path | None, **kwargs):
    """Run deductive fault simulator."""

    # extend positional arguments
    # with lines from file, if given
    extend_from_file(input_vectors, file)

    # Create the deductive fault simulator for this circuit
    sim = FaultSimulation(net_file)

    # Run multiple test vectors with the same object
    # and print the output nicely
    for test in input_vectors:
        print(f'Circuit: {net_file.as_posix()}')
        print('Input Vector: ' + ' '.join(test))

        faults = sim.detect_faults(test)

        print(f'------ Detected Faults ({len(faults)}) ------')
        for f in sorted(faults):
            print(f'{f.net_id:>4} stuck at {f.stuck_at}')
        print()
    print(flush=True)
