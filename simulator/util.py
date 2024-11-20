"""Standalone utility functions and techniques useful for testing"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator

    from .structs import Logic

from . import structs as _structs


def random_patterns(length: int) -> Generator[str]:
    """
    Simple Linear Congruential generator to generate all possible bitstring patterns with `length`
    https://en.wikipedia.org/wiki/Linear_congruential_generator
    https://stackoverflow.com/a/65753338

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
    Return the input vector string as a list of Logic values
    """

    if not all(char in '01' for char in string):
        raise TypeError("Input string must contain only '0's and '1's.")

    # Convert the string to a list of boolean values
    # Logic.High and Logic.Low can be constructed from '1' and '0' respectively
    return [_structs.Logic(char) for char in string]


def logic_to_bitstring(vector: list[Logic]) -> str:
    """
    Convert a list of Logic values into a bitstring representation
    String should contain only '0', '1' or 'X'.
    """
    output_str = ''.join(str(v) for v in vector)
    return output_str
