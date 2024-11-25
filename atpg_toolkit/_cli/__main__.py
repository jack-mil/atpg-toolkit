from argparse import ArgumentParser

from .._version import __version__
from .faults import faults_cmd
from .generate import generate_cmd
from .simulate import simulate_cmd


def main():
    parser = ArgumentParser(
        description='Generate test patterns or simulate faults on digital logic circuits.',
        epilog='jack-mil (2024) https://github.com/jack-mil/logic-test-generator',
    )
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    subparses = parser.add_subparsers(title='Actions', required=True)
    subparses.add_parser(
        'faults',
        aliases=['f'],
        add_help=False,
        parents=[faults_cmd],
        description=faults_cmd.description,
        help=faults_cmd.description,
    )
    subparses.add_parser(
        'generate',
        aliases=['g'],
        add_help=False,
        parents=[generate_cmd],
        description=generate_cmd.description,
        help=generate_cmd.description,
    )
    subparses.add_parser(
        'simulate',
        aliases=['s'],
        add_help=False,
        parents=[simulate_cmd],
        description=simulate_cmd.description,
        help=simulate_cmd.description,
    )
    args = parser.parse_args()
    args.func(**vars(args))

if __name__ == "__main__":
    main()
