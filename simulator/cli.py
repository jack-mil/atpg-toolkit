"""
Circuit Simulator and Deductive Fault Simulator entry point and command line interface.
This module shows how to use the `simulator` and `circuit` module API.
"""

from argparse import Namespace
from pathlib import Path

from .simulator import Simulation


def main():
    args = parse_args()
    print(f'Netlist file: {args.net_file}:')

    # support a single input vector from cli arguments,
    # or read multiple vectors from a file
    if args.input_file:
        with args.input_file.open() as fp:
            tests = [line.rstrip() for line in fp if line]
    else:
        tests = [args.input_vector]

    # Create the simulation object from this circuit
    circuit = Simulation(args.net_file)

    # Run multiple test vectors with the same object
    # and print the output nicely
    print(f"{'Inputs'.ljust(len(tests[0]))} | {'Outputs'} ")
    for test in tests:
        out = circuit.simulate_input(test)
        print(f'{test} | {out}')
    print()


def parse_args() -> Namespace:
    """Command line interface definition for interactive usage"""

    from argparse import ArgumentParser, ArgumentTypeError

    def valid_path(name):
        p = Path(name)
        if not p.is_file():
            raise ArgumentTypeError(f'file "{name}" does not exist')
        return p

    parser = ArgumentParser(
        description='Perform a logic simulation with a given netlist and test vector(s)'
    )
    parser.add_argument('net_file', type=valid_path, help='Netlist file to simulate')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        'input_vector',
        type=str,
        nargs='?',
        help='A single test vector string',
    )
    group.add_argument(
        '-i',
        '--input-file',
        type=valid_path,
        help='Path to a file containing multiple input vector strings',
    )

    return parser.parse_args()


if __name__ == '__main__':
    main()
