# SPDX-FileCopyrightText: 2024 jack-mil
#
# SPDX-License-Identifier: MIT

"""
Command line interface commands for interactive usage
of the Fault Simulator and PODEM Test Generator.

This module also demonstrates usage of the library API.
"""

from __future__ import annotations

import sys
from argparse import ArgumentParser
from pathlib import Path

from atpg_toolkit.__about__ import copyright, version
from atpg_toolkit.cli.fault_app import faults_cmd
from atpg_toolkit.cli.podem_app import generate_cmd
from atpg_toolkit.cli.simulate_app import simulate_cmd


def main():
    parser = ArgumentParser(
        description='Generate test patterns or simulate faults on digital logic circuits.',
        epilog=f'{copyright}. Source: https://github.com/jack-mil/atpg-toolkit',
        prog=Path(sys.argv[0]).name,
    )
    # Python >=3.14 features
    parser.suggest_on_error = True
    parser.color = True

    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {version}')
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
