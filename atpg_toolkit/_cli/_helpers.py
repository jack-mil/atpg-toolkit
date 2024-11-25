from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import ArgumentParser
    from collections.abc import Callable

from argparse import ArgumentTypeError
from pathlib import Path


def valid_path(name) -> Path:
    """Validate paths used in command line arguments."""
    p = Path(name)
    if not p.is_file():
        raise ArgumentTypeError(f'file "{name}" does not exist')
    return p


def max_len(iterable) -> int:
    """
    Get the length of longest item in the collection.
    Useful for printing with alignment.
    """
    return max(len(s) for s in iterable)


def extend_from_file(collection, file: Path | None):
    """Read lines from a file, and append them to existing collection."""
    if file is not None:
        with file.open() as fp:
            collection.extend([line.strip() for line in fp if line])
    return collection


def add_action(parser: ArgumentParser):
    """Assign a function as the default callable for 'func' argument of this parser."""

    def decorator(function: Callable):
        parser.set_defaults(func=function)
        return function

    return decorator
