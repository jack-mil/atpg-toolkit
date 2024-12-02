from __future__ import annotations

from os import PathLike

type NetId = int | str
"""A net can be referred to by a integer or a string"""

type StrPath = str | PathLike[str]
"""String or path-like objects"""

class NetlistFormatError(Exception):
    """Raised when circuit net-list is malformed or invalid."""

class InvalidNetError(Exception):
    """Raised when there is a circuit/fault mismatch."""
