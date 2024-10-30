from argparse import Namespace
from pathlib import Path

from .circuit import Circuit


def main():
    args = parse_args()
    print(f'Netlist file: {args.net_file}:')

    if args.input_file:
        with args.input_file.open() as fp:
            tests = [line.rstrip() for line in fp if line]
    else:
        tests = [args.input_vector]

    circuit = Circuit(args.net_file)

    print(f"{'Inputs'.ljust(len(tests[0]))} | {'Outputs'} ")
    for test in tests:
        out = circuit.evaluate_input(test)
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
