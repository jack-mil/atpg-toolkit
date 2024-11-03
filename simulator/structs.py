"""
Structures and enum data definitions for utility in the simulation module
"""

from dataclasses import dataclass
from enum import Enum, StrEnum

__all__ = ['GateType', 'Logic', 'Gate']


class Logic(Enum):
    HIGH = True
    LOW = False
    UNASSIGNED = None

    def __bool__(self) -> bool:
        """Override the bool() behavior to allow boolean operations valid Logic variants"""
        if self.value is None:
            raise RuntimeError(
                'Attempted boolean evaluation of unassigned Logic.\n This is probably unintended.'
            )
        return self.value is True

    def __str__(self) -> str:
        match self:
            case Logic.HIGH:
                return '1 (High)'
            case Logic.LOW:
                return '0 (Low)'
            case Logic.UNASSIGNED:
                return 'Unassigned'


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

    def evaluate(self, *inputs: Logic) -> Logic:
        """
        Stateless boolean logic output evaluation
        based on this gate type
        """
        match self.type_, inputs:
            case GateType.INV, (a,):
                return Logic(not a)
            case GateType.BUF, (a,):
                return Logic(a)
            case GateType.AND, (a, b):
                return Logic(a and b)
            case GateType.OR, (a, b):
                return Logic(a or b)
            case GateType.NOR, (a, b):
                return Logic(not (a or b))
            case GateType.NAND, (a, b):
                return Logic(not (a and b))
            case _:
                raise TypeError(f'Could not evaluate gate {self}')
