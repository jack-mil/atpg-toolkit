# SPDX-FileCopyrightText: 2024 jack-mil
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import ArgumentParser
    from collections.abc import Callable, Collection, MutableSequence, Sized

    from atpg_toolkit.types import StrPath

from argparse import ArgumentTypeError
from pathlib import Path


def valid_path(name: StrPath) -> Path:
    """Validate paths used in command line arguments."""
    p = Path(name)
    if not p.is_file():
        raise ArgumentTypeError(f'file "{name}" does not exist')
    return p


def max_len(collection: Collection[Sized]) -> int:
    """
    Get the length of longest item in the collection.
    Useful for printing with alignment.
    """
    return max(map(len, collection))


def extend_from_file[T: MutableSequence[str]](sequence: T, file: Path | None) -> T:
    """Read lines from a file, and append them to and existing mutable sequence."""
    if file is not None:
        with file.open() as fp:
            sequence.extend(line.strip() for line in fp if line)
    return sequence


def add_action[F: Callable[..., None]](parser: ArgumentParser) -> Callable[[F], F]:
    """Assign a function as the default callable for 'func' argument of this parser."""

    def decorator(function: F) -> F:
        parser.set_defaults(func=function)
        return function

    return decorator
