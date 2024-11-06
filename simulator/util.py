"""Standalone utility functions and techniques useful for testing"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Generator


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
