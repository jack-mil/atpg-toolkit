"""
Structures and enum data definitions for utility in the simulation module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal

    from .types import NetId

from dataclasses import dataclass, field
from enum import Enum, StrEnum

__all__ = ['Fault', 'Gate', 'GateType', 'Logic']


class MultiValueEnum(Enum):
    # https://docs.python.org/3/howto/enum.html#multivalueenum
    # requires Python 3.13
    def __new__(cls, value, *values):
        it = object.__new__(cls)
        it._value_ = value
        for v in values:
            it._add_value_alias_(v)  # type: ignore
        return it


class Logic(MultiValueEnum):
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

    def __xor__(self, other) -> Literal[Logic.Low, Logic.High]:
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

    def __str__(self) -> str:
        """String representation."""  # noqa: D401
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
        pass

    def __str__(self) -> str:
        """Format a Fault as a string (1-sa-0)."""
        return f'{self.net_id}-sa-{self.stuck_at}'


class GateType(StrEnum):
    """
    Supported gate types.
    Used internally by the `Gate` class.
    """

    Inv = 'INV'
    Buf = 'BUF'
    And = 'AND'
    Or = 'OR'
    Nor = 'NOR'
    Nand = 'NAND'

    def __repr__(self):
        return f'<{self.name}>'

    def min_inputs(self):
        """Get the minimum number of inputs for each type of gates."""
        match self:
            case GateType.Inv | GateType.Buf:
                return 1
            case _:
                return 2

    def control_value(self):
        """Get the controlling value for each type of gate."""
        match self:
            case GateType.And | GateType.Nand:
                return Logic.Low
            case GateType.Or | GateType.Nor:
                return Logic.High
            case GateType.Buf | GateType.Inv:
                return None
            case _:
                raise TypeError(f'Gate type unknown: {self}')

    def inversion(self):
        """Get the inversion parity for each types of gate."""
        match self:
            case GateType.And | GateType.Or | GateType.Buf:
                return Logic.Low
            case GateType.Nand | GateType.Nor | GateType.Inv:
                return Logic.High


@dataclass(eq=True, frozen=True)
class Gate:
    """
    A Gate representation has an associated logic type,
    a single output net id, and 1 or more input net ids.

    A Gate is hashable and considered equal when the type
    and associated net ids are equivalent.

    """

    type_: GateType
    inputs: tuple[NetId, ...]
    output: NetId

    def __post_init__(self):
        """Validate the Gate struct at object creation."""
        if len(self.inputs) < (n := self.type_.min_inputs()):
            raise TypeError(f'Gate of type {self.type_} must have >= {n} inputs')

    def evaluate(self, *input_states: Logic) -> Logic:
        """
        Stateless boolean logic output evaluation
        based on this gate type. Utilizes the overridden bitwise operators.
        """
        match self.type_, input_states:
            case GateType.Inv, (state,):
                return ~state
            case GateType.Buf, (state,):
                return state
            case GateType.And, (state_a, state_b):
                return state_a & state_b
            case GateType.Or, (state_a, state_b):
                return state_a | state_b
            case GateType.Nor, (state_a, state_b):
                return ~(state_a | state_b)
            case GateType.Nand, (state_a, state_b):
                return ~(state_a & state_b)
            case _:
                raise TypeError(f'Gate {self} not supported')

    def control_value(self) -> Literal[Logic.Low, Logic.High] | None:
        """Get the control value for this type of Gate. None if it doesn't have one."""
        return self.type_.control_value()

    def inversion(self) -> Literal[Logic.Low, Logic.High]:
        """
        Get the inversion value for this type of Gate.
        - AND, OR, and BUF have parity 0
        - NAND, NOR, and INV have parity 1.
        """
        return self.type_.inversion()
