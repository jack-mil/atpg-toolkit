"""
Definition of the supported logic gate types, and their properties.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal

    from .types import NetId

from dataclasses import dataclass
from enum import StrEnum

from .logic import Logic

__all__ = ['Gate', 'GateType']


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
