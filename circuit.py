from pathlib import Path
from enum import StrEnum, Enum
from dataclasses import dataclass


class GateType(StrEnum):
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
    and associated net ids are equivalent
    """

    type: GateType
    inputs: tuple[int, ...]
    output: int


class Logic(Enum):
    HIGH = True
    LOW = False
    UNASSIGNED = None

    def __repr__(self):
        return f'<Logic.{self.name}>'


class Circuit:
    """A circuit is composed of a list of gates and a net-list where each net has an associated state.

    The Circuit class keeps track of the current state of all the nets.

    The Circuit also has associated input and output nets.
    The Circuit is initialized from a net-list file in a particular format"""

    def __init__(self, netlist_file: Path):
        """Create a new Circuit representation from the given net-list definition file."""

        self._file = Path(netlist_file)
        """The circuit definition file"""

        if not self._file.exists():
            raise RuntimeError(f'Netlist file "{self._file}" could not be found')

        self._inputs: list[int] = []
        """List of circuit input net ids"""

        self._outputs: list[int] = []
        """List of circuit output net ids"""

        self._gates: set[Gate] = set()
        """Set of all logic Gates in this circuit"""

        self._net_states: dict[int, Logic] = {}
        """Mapping of all net ids in this circuit, and the associated logic state (HIGH, LOW, UNASSIGNED)."""

        self.load_state_from_file()

    def load_state_from_file(self):
        """
        Read from the associated netlist file,
        and setup the initial circuit state
        """
        with self._file.open() as f:
            # prefilter blank lines
            lines = [line.rstrip() for line in f if line]

        # each should be in the format 'GATE_TYPE [1-2 input nets] [1 output net]'
        # e.g. "INV 9 5" or "NAND 16 17 14"
        # The last two lines are special INPUT and OUTPUT net definitions
        # e.g. INPUT  1 2 3 4 6 8 10 -1  <- -1 can be ignores
        #      OUTPUT  7 9 11 5 -1

        for line in lines:  # process line
            keyword, *nets = line.split()  # split on whitespace
            nets = list(map(int, nets))  # map all net id's to numbers

            if keyword in GateType:
                # add each net id we encounter to the internal dictionary. Some may repeat, that's ok
                self._net_states.update((net, Logic.UNASSIGNED) for net in nets)
                # the last net id in the line is the gate output net
                *in_ids, out_id = nets
                # Create a new gate and add it to internal set
                self._gates.add(
                    Gate(
                        type=GateType(keyword),
                        output=out_id,
                        inputs=tuple(in_ids),
                    )
                )

            elif keyword == 'INPUT':
                *in_ids, _ = nets
                self.validate_nets(in_ids)
                self._inputs.extend(in_ids)

            elif keyword == 'OUTPUT':
                *out_ids, _ = nets
                self.validate_nets(out_ids)
                self._outputs.extend(out_ids)

            else:
                raise RuntimeError(f'Unknown gate type {keyword} in line: {line}')

    def validate_nets(self, net_ids):
        """Check to make sure that all given net_ids exist in this circuit."""
        missing_keys = set(net_ids) - self._net_states.keys()
        if len(missing_keys) > 0:
            raise RuntimeError(
                f'Undefined input net(s) encountered. Nets: "{missing_keys}" not found net-list'
            )

    @property
    def outputs(self):
        output_str = ''
        for net_id in self._outputs:
            match self._net_states[net_id]:
                case Logic.HIGH:
                    output_str += '1'
                case Logic.LOW:
                    output_str += '0'
                case Logic.UNASSIGNED:
                    output_str += '?'
        return output_str
