# SPDX-FileCopyrightText: 2024 jack-mil
#
# SPDX-License-Identifier: MIT

"""
Definition of the 5-valued Logic type and boolean operations,
and the Fault dataclass to represent single-stuck faults.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, assert_never, override

if TYPE_CHECKING:
    from typing import Literal

__all__ = ['Fault', 'Logic']


class _MultiValueEnum(Enum):
    # https://docs.python.org/3/howto/enum.html#multivalueenum
    # requires Python 3.13
    def __new__(cls, value, *values):
        it = object.__new__(cls)
        it._value_ = value
        for v in values:
            # Pylance missing this attribute for some reason?
            it._add_value_alias_(v)  # type: ignore[reportAttributeAccessIssue]
        return it


class Logic(_MultiValueEnum):
    """
    Enum to represent a net logic level (voltage state).

    - Bitwise logical operators | & ~ are defined to evaluate 5-state logic.

    - Bitwise ^ (XOR) is defined for High and Low variants only.

    High and Low variants represent 1 and 0
    X : net with unknown/no logic level (NOT "don't care")
    D : faulty net at 0 instead of 1
    D̅ : faulty net at 1 instead of 0
    """

    High = '1', 1, True
    """Logical 1"""
    Low = '0', 0, False
    """Logical 0"""
    D = 'D'
    """Faulty 0 instead of 1 (SA0)"""
    Dbar = 'D̅'
    """(D̅) Faulty 1 instead of 0 (SA1)"""
    X = 'X'
    """A undefined/unknown logic state"""

    def __bool__(self) -> bool:
        """Disable bool() (`not`) to prevent bugs. Use the bitwise operators to combine and evaluate logic values."""
        return NotImplemented

    def __invert__(self) -> Logic:
        """Bitwise ~ operator. Override to return the opposite Logic value."""
        match self:
            case Logic.Low:
                return Logic.High
            case Logic.High:
                return Logic.Low
            case Logic.D:
                return Logic.Dbar
            case Logic.Dbar:
                return Logic.D
            case Logic.X:
                return Logic.X
            case _:
                assert_never()

    def __or__(self, other) -> Logic:
        """Bitwise | operator. Override to evaluate OR operations on Logic type."""
        if not isinstance(other, Logic):
            return NotImplemented

        # order of these checks matter
        # might be clearer & faster with a LUT
        if (self is Logic.High) or (other is Logic.High):
            return Logic.High

        if (self is Logic.X) or (other is Logic.X):
            return Logic.X

        if self is Logic.Low:
            return Logic(other)

        if other is Logic.Low:
            return Logic(self)

        if self is other:
            # both D or both Dbar
            return Logic(self)
        else:
            # one D, one Dbar
            return Logic.High

    def __and__(self, other) -> Logic:
        """Bitwise & operator. Override to evaluate AND operation on Logic type."""
        if not isinstance(other, Logic):
            return NotImplemented

        # order of these checks matter
        if (self is Logic.Low) or (other is Logic.Low):
            return Logic.Low

        if (self is Logic.X) or (other is Logic.X):
            return Logic.X

        if self is Logic.High:
            return Logic(other)

        if other is Logic.High:
            return Logic(self)

        if self is other:
            # Both D or both Dbar
            return Logic(self)
        else:
            # one D, one Dbar
            return Logic.Low

    def __xor__(self, other: object) -> Literal[Logic.Low, Logic.High]:
        if not isinstance(other, Logic):
            return NotImplemented

        if self is not Logic.Low and self is not Logic.High:
            return NotImplemented

        if other is not Logic.Low and other is not Logic.High:
            return NotImplemented

        if self is other:
            return Logic.Low
        else:
            return Logic.High

    @override
    def __str__(self) -> str:
        """Represent as a string."""

        return self.value


@dataclass(eq=True, frozen=True, order=True)
class Fault:
    """
    Represent a net with a single stuck-at fault.
    TODO: Make this a regular class instead of dataclass,
    just implement hashable and order, etc.
    Less complicated than working around dataclass validation.
    Would also simplify constructing Logic type.
    """

    net_id: str | int
    """Net (node) id of the fault"""
    stuck_at: Logic = field(hash=True, compare=False)
    """Logic stuck at level (High or Low)"""

    def __post_init__(self):
        """
        Validate the Fault struct at object creation.
        See: https://docs.python.org/3/library/dataclasses.html#frozen-instances.
        """
        if not isinstance(self.stuck_at, Logic):
            object.__setattr__(self, 'stuck_at', Logic(self.stuck_at))
        if (self.stuck_at is not Logic.Low) and (self.stuck_at is not Logic.High):
            raise TypeError('Stuck at must be set to a High or Low Logic value')

    @override
    def __str__(self) -> str:
        """Format a Fault as a string (1-sa-0)."""
        return f'{self.net_id}-sa-{self.stuck_at}'
