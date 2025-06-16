# SPDX-FileCopyrightText: 2024 jack-mil
#
# SPDX-License-Identifier: MIT

"""Standalone utility functions and techniques useful for testing."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import atpg_toolkit.logic as _logic

if TYPE_CHECKING:
    from collections.abc import Generator

    from atpg_toolkit.logic import Fault, Logic


FAULT_REGEX = re.compile(r'^(\S+)-sa-([01])$')
"""Patterns to validate a string representation of a fault"""
ALT_FAULT_REGEX = re.compile(r'^(\S+)\s+([01])$')


def try_as_int(value: int | str) -> int | str:
    """Compatibility from when net id's where always Int."""
    try:
        return int(value)
    except ValueError:
        return value


def str_to_fault(fault_str: str) -> Fault | None:
    """Convert a string of format [net-id]-sa[0|1] to a valid Fault object."""
    for pat in (FAULT_REGEX, ALT_FAULT_REGEX):
        result = pat.match(fault_str)
        if result is not None:
            break
    else:
        return None
    net_id, value = result.groups()
    fault = _logic.Fault(try_as_int(net_id), _logic.Logic(value))
    return fault


def random_patterns(length: int) -> Generator[str]:
    """
    Generate all possible bitstring patterns of `length` using a simple Linear Congruential generator.

    - https://en.wikipedia.org/wiki/Linear_congruential_generator
    - https://stackoverflow.com/a/65753338

    Parameters are chosen to ensure a period of length n, with no repeats.
    """
    import random

    n = 2**length  # modulus (m)
    c = 1  # increment
    a = 5  # multiplier
    # Use a random start value every invocation
    num = random.randrange(0, n)
    for _ in range(n):
        num = (a * num + c) % n
        yield f'{num:0{length}b}'


def bitstring_to_logic(string: str) -> list[Logic]:
    """
    Check if the string contains only '0's and '1's.
    Return the input vector string as a list of Logic values.
    """

    if not all(char in '01X' for char in string):
        raise TypeError("Input string must contain only '0's, '1's and X's")

    # Convert the string to a list of boolean values
    # Logic.High and Logic.Low can be constructed from '1' and '0' respectively
    return [_logic.Logic(char) for char in string]


def logic_to_bitstring(vector: list[Logic]) -> str:
    """
    Convert a list of Logic values into a bitstring representation.
    String should contain only '0', '1' or 'X'.
    """
    output_str = ''.join(str(v) for v in vector)
    return output_str
