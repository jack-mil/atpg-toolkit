"""
Structures and enum data definitions for utility in the simulation module
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, StrEnum

__all__ = ['GateType', 'Logic', 'Gate', 'Fault']


class Logic(Enum):
    HIGH = True
    LOW = False
    UNASSIGNED = None

    def __bool__(self) -> bool:
        """Disable bool() (`not`) to prevent bugs. Use the bitwise operators to combine and evaluate logic values"""
        return NotImplemented

    def __invert__(self) -> Logic:
        """Bitwise ~ operator. Override to return the opposite Logic value"""
        if self.value is None:
            raise ValueError(
                'Attempted boolean evaluation of unassigned Logic.\n This is probably unintended.'
            )
        return Logic(not self.value)

    def __or__(self, other) -> Logic:
        """Bitwise | operator. Override to evaluate OR operations on Logic type"""
        if not isinstance(other, Logic):
            return NotImplemented
        if self.value is None:
            raise ValueError(
                'Attempted boolean evaluation of unassigned Logic.\n This is probably unintended.'
            )
        return Logic(self.value or other.value)

    def __and__(self, other) -> Logic:
        """Bitwise & operator. Override to evaluate AND operation on Logic type"""
        if not isinstance(other, Logic):
            return NotImplemented
        if self.value is None:
            raise ValueError(
                'Attempted boolean evaluation of unassigned Logic.\n This is probably unintended.'
            )
        return Logic(self.value and other.value)

    def __str__(self) -> str:
        match self:
            case Logic.HIGH:
                return '1 (High)'
            case Logic.LOW:
                return '0 (Low)'
            case Logic.UNASSIGNED:
                return 'Unassigned'


@dataclass(eq=True, frozen=True)
class Fault:
    """Represent a single stuck-at fault on given net."""

    net_id: int
    stuck_at: Logic

    def __post_init__(self):
        """Validate the Fault struct at object creation"""
        if not isinstance(self.stuck_at, Logic):
            raise TypeError("stuck at value must be a 'Logic' type")
        if self.stuck_at is Logic.UNASSIGNED:
            raise TypeError('stuck at mush be set to a High or Low Logic value')

    def __str__(self) -> str:
        return f'{self.net_id}-sa-{self.stuck_at}'


class GateType(StrEnum):
    """
    Supported gate types.
    Used internally by the `Gate` class.
    """

    INV = 'INV'
    BUF = 'BUF'
    AND = 'AND'
    OR = 'OR'
    NOR = 'NOR'
    NAND = 'NAND'

    def __repr__(self):
        return f'<{self.name}>'


@dataclass(eq=True, frozen=True)
class Gate:
    """
    A Gate representation has an associated logic type,
    a single output net id, and 1 or more input net ids.

    A Gate is hashable and considered equal when the type
    and associated net ids are equivalent.

    """

    type_: GateType
    inputs: tuple[int, ...]
    output: int

    def evaluate(self, *input_states: Logic) -> Logic:
        """
        Stateless boolean logic output evaluation
        based on this gate type. Utilizes the overridden bitwise operators.
        """
        match self.type_, input_states:
            case GateType.INV, (state,):
                return ~state
            case GateType.BUF, (state,):
                return state
            case GateType.AND, (state_a, state_b):
                return state_a & state_b
            case GateType.OR, (state_a, state_b):
                return state_a | state_b
            case GateType.NOR, (state_a, state_b):
                return ~(state_a | state_b)
            case GateType.NAND, (state_a, state_b):
                return ~(state_a & state_b)
            case _:
                raise TypeError(f'Could not evaluate gate {self}')

