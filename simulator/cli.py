"""
Command line interface and interactive entry-point
for the Fault Simulator and PODEM Test Generator.
This module shows how to use the `simulator` and `circuit` module API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import Namespace
    from pathlib import Path

from . import util
from .faultsim import FaultSimulation
from .podem import TestGenerator
from .simulator import Simulation


def main():
    args = parse_args()

    # support a single input vector from cli arguments,
    # or read multiple vectors from a file
    if args.command == 'generate':
        generate(args.net_file, args.faults)
    else:
        if args.input_file:
            with args.input_file.open() as fp:
                tests = [line.rstrip() for line in fp if line]
        else:
            tests = [args.input_vector]

        if args.command == 'simulate':
            simulate(args.net_file, tests)
        elif args.command == 'faults':
            deduce(args.net_file, tests)


def simulate(net_file: Path, tests: list[str]):
    """Run fault-free circuit simulator."""

    # Create the simulation object for this circuit
    circuit = Simulation(net_file)

    # Run multiple test vectors with the same object
    # and print the output nicely
    print(f'Circuit: {net_file}')
    print(f'{"Inputs".ljust(len(tests[0]))} | {"Outputs"}')
    for test in tests:
        out = circuit.simulate_input(test)
        print(f'{test} | {out}')
    print()


def deduce(net_file: Path, tests: list[str]):
    """Run deductive fault simulator."""

    # Create the deductive fault simulator for this circuit
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


def generate(net_file: Path, target_faults: list[str]):
    """Generate a test vector for fault in format '[net-id]-sa-[0 | 1]'. e.g. 2-sa-0."""

    import sys

    # pre-process the list of faults to turn into list of Faults
    faults = []
    for string in target_faults:
        fault = util.str_to_fault(string)
        if fault is None:
            print(f'Fault {string!r} is invalid.', file=sys.stderr)
            print(
                'Format: [net-id]-sa[0|1]. E.g. 2-sa-0, net123-sa-0, etc.',
                file=sys.stderr,
            )
            exit(1)
        faults.append(fault)
    faults.sort()

    # Create the PODEM ATP Generator for this net-circuit
    gen = TestGenerator(net_file)

    width = max(len(s) for s in target_faults)
    print(f'Circuit: {net_file}')
    print(f'{"Fault".ljust(width)} | Test')
    for fault in faults:
        test = gen.generate_test(fault)
        print(f'{f"{fault}":<{width}} | {test if test else "UNDETECTABLE"}')
    print(flush=True)


def parse_args() -> Namespace:
    """Command line interface definition for interactive usage."""

    from argparse import ArgumentParser, ArgumentTypeError
    from pathlib import Path

    def valid_path(name) -> Path:
        p = Path(name)
        if not p.is_file():
            raise ArgumentTypeError(f'file "{name}" does not exist')
        return p

    parser = ArgumentParser(description='Perform simulation or find detected faults.')

    subparsers = parser.add_subparsers(dest='command', required=True, description='The action to perform.')

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

    # Subcommand 'generate'
    podem_parser = subparsers.add_parser('generate', help='Find a test vector that detects the given fault')
    podem_parser.add_argument('net_file', type=valid_path, help='Net-list file (circuit) to test')
    podem_parser.add_argument('faults', nargs='+', help='One or more faults to generate tests for (5-sa0)')

    return parser.parse_args()


if __name__ == '__main__':
    main()
