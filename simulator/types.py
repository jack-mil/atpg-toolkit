from __future__ import annotations

from os import PathLike

type NetId = int | str
"""A net can be referred to by a integer or a string"""

type StrPath = str | PathLike[str]
"""String or path-like objects"""
