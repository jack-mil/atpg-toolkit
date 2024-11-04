"""
Circuit Simulator and Deductive Fault Simulator entry point and command line interface.
This module shows how to use the `simulator` and `circuit` module API.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import Namespace
    from pathlib import Path

from .simulator import Simulation
from .faultsim import FaultSimulation


def main():
    args = parse_args()

    # support a single input vector from cli arguments,
    # or read multiple vectors from a file
    if args.input_file:
        with args.input_file.open() as fp:
            tests = [line.rstrip() for line in fp if line]
    else:
        tests = [args.input_vector]

    if args.command == 'simulate':
        simulate(args.net_file, tests)
    if args.command == 'faults':
        deduce(args.net_file, tests)


def simulate(net_file: Path, tests: list[str]):
    # Create the simulation object from this circuit
    circuit = Simulation(net_file)

    # Run multiple test vectors with the same object
    # and print the output nicely
    print(f'Circuit: {net_file}')
    print(f"{'Inputs'.ljust(len(tests[0]))} | {'Outputs'} ")
    for test in tests:
        out = circuit.simulate_input(test)
        print(f'{test} | {out}')
    print()


def deduce(net_file: Path, tests: list[str]):
    # Create the deductive fault simulator from this netlist
    sim = FaultSimulation(net_file)

    # Run multiple test vectors with the same object
    # and print the output nicely
    for test in tests:
        print(f'Circuit: {net_file}')
        print(f'Input Vector: {" ".join(test)}')
        faults = sim.detect_faults(test)
        print(f'------ Detected Faults ({len(faults)}) ------')
        for f in sorted(faults):
            print(f'{f.net_id:>4} stuck at {f.stuck_at}')
        print()
    print(flush=True)


def parse_args() -> Namespace:
    """Command line interface definition for interactive usage"""

    from argparse import ArgumentParser, ArgumentTypeError

    def valid_path(name):
        p = Path(name)
        if not p.is_file():
            raise ArgumentTypeError(f'file "{name}" does not exist')
        return p

    parser = ArgumentParser(description='Perform simulation or find detected faults.')

    subparsers = parser.add_subparsers(
        dest='command', required=True, description='The action to perform.'
    )

    def add_common_arguments(parser):
        parser.add_argument('net_file', type=valid_path, help='Net-list file (circuit) to simulate')
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            'input_vector',
            type=str,
            nargs='?',
            help='A single test vector string',
        )
        group.add_argument(
            '-f',
            '--input-file',
            type=valid_path,
            help='Path to a file containing multiple input vector strings',
        )

    # Subcommand 'simulate'
    simulate_parser = subparsers.add_parser(
        'simulate', help='Perform fault-free simulation with a given net-list and test vector(s)'
    )
    add_common_arguments(simulate_parser)

    # Subcommand 'faults'
    faults_parser = subparsers.add_parser(
        'faults', help='Find detected faults with a given net-list and test vector(s)'
    )
    add_common_arguments(faults_parser)

    return parser.parse_args()


if __name__ == '__main__':
    main()
