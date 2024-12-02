from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

from argparse import ArgumentParser

from .. import util
from ..podem import InvalidNetError, TestGenerator
from ._helpers import add_action, extend_from_file, max_len, valid_path

# subcommand 'generate'
generate_cmd = ArgumentParser(
    description='Find a test vector that detects a given fault',
)
generate_cmd.add_argument(
    'net_file',
    type=valid_path,
    help='Net-list file (circuit) to test',
)
generate_cmd.add_argument(
    '-f',
    '--file',
    required=False,
    type=valid_path,
    help='path to a file containing additional test vector strings',
)
generate_cmd.add_argument(
    'faults',
    nargs='*',
    help='One or more faults to generate tests for (e.g. 5-sa-0)',
)


@add_action(generate_cmd)
def generate(net_file: Path, faults: list[str], file: Path | None, **kwargs):
    """Generate a test vector for fault in format '[net-id]-sa-[0 | 1]'. e.g. 2-sa-0."""

    import sys

    # extend positional arguments
    # with lines from file, if given
    extend_from_file(faults, file)

    # pre-process the list of faults to turn into list of Faults
    fault_list = []
    for string in faults:
        fault = util.str_to_fault(string)
        if fault is None:
            print(f'Fault {string!r} is invalid.', file=sys.stderr)
            print(
                'Format: [net-id]-sa[0|1]. E.g. 2-sa-0, net123-sa-0, etc.',
                file=sys.stderr,
            )
            exit(1)
        fault_list.append(fault)
    fault_list.sort()

    # Create the PODEM ATP Generator for this net-circuit
    gen = TestGenerator(net_file)

    width = max_len(faults)
    print(f'Circuit: {net_file.as_posix()}')
    print('Fault'.ljust(width) + ' | Test')

    for fault in fault_list:
        try:
            test = gen.generate_test(fault)
        except InvalidNetError:
            print(f'{f"{fault}":<{width}} | NON-EXISTENT')
        else:
            print(f'{f"{fault}":<{width}} | {test if test else "UNDETECTABLE"}')
    print(flush=True)
