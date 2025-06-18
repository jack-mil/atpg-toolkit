# SPDX-FileCopyrightText: 2024 jack-mil
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

from argparse import ArgumentParser

from atpg_toolkit.cli._helpers import add_action, extend_from_file, max_len, valid_path
from atpg_toolkit.simulator import Simulation

# subcommand 'simulate'
simulate_cmd = ArgumentParser(
    description='Perform fault-free simulation with a given net-list and test vector(s)',
)
simulate_cmd.add_argument(
    'net_file',
    type=valid_path,
    help='Net-list file (circuit) to simulate',
)
simulate_cmd.add_argument(
    '-f',
    '--file',
    required=False,
    type=valid_path,
    help='path to a file containing additional input vector strings',
)
simulate_cmd.add_argument(
    'input_vectors',
    nargs='*',
    help='One or more input vectors to simulate',
)


@add_action(simulate_cmd)
def simulate(net_file: Path, input_vectors: list[str], file: Path | None, **kwargs):  # noqa: ARG001
    """Run fault-free circuit simulator."""

    # extend positional arguments
    # with lines from file, if given
    extend_from_file(input_vectors, file)

    # Create the simulation object for this circuit
    circuit = Simulation(net_file)

    # Run multiple test vectors with the same object
    # and print the output nicely
    width = max_len(input_vectors)
    print(f'Circuit: {net_file.as_posix()}')
    print('Inputs'.ljust(width) + ' | Outputs')

    for vector in input_vectors:
        out = circuit.simulate_input(vector)
        print(f'{vector} | {out}')
    print(flush=True)
