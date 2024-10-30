from pathlib import Path
from enum import StrEnum, Enum
from dataclasses import dataclass
from typing import Collection


class GateType(StrEnum):
    INV = 'INV'
    BUF = 'BUF'
    AND = 'AND'
    OR = 'OR'
    NOR = 'NOR'
    NAND = 'NAND'

    def __repr__(self):
        return f'<{self.name}>'


class Logic(Enum):
    HIGH = True
    LOW = False
    UNASSIGNED = None

    def __bool__(self) -> bool:
        """Override the bool() behavior to allow boolean operations valid Logic variants"""
        if self.value is None:
            raise RuntimeError(
                'Attempted boolean evaluation of unnasigned Logic.\n This is probably unintended.'
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

    def evaluate(self, *inputs: Logic) -> Logic:
        """
        Stateless boolean logic output evaluation
        based on this gate type
        """
        match self.type, inputs:
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
                self._inputs.extend(self.validate_nets(in_ids))

            elif keyword == 'OUTPUT':
                *out_ids, _ = nets
                self._outputs.extend(self.validate_nets(out_ids))

            else:
                raise RuntimeError(f'Unknown gate type {keyword} in line: {line}')

    def validate_nets(self, net_ids: Collection[int]) -> Collection[int]:
        """Check to make sure that all given net_ids exist in this circuit."""
        missing_keys = set(net_ids) - self._net_states.keys()
        if len(missing_keys) > 0:
            raise RuntimeError(
                f'Undefined input net(s) encountered. Nets: "{missing_keys}" not found net-list'
            )
        return net_ids

    def evaluate_input(self, input_vector: str):
        """
        With a valid input vector,
        evaluate the circuit logic,
        and return the resulting output net vector
        """
        vector = self.validate_input_string(input_vector)

        # Initialize the input nets with the input vector values
        # print('Initial input states: ')
        for net_id, state in zip(self._inputs, vector):
            # print(f'Input Net {net_id}: {state}')
            self._net_states[net_id] = state

        gates_to_process = self._gates.copy()
        # simulate until every gate has been evaluated
        while len(gates_to_process) > 0:
            ready_gates = self.find_ready_gates(gates_to_process)

            for gate in ready_gates:
                output_state = self.evaluate_gate_output(gate)
                # evaluate the result of the gate inputs and update the net-list state
                self._net_states[gate.output] = output_state
                # print(f'Gate {gate.type} net {gate.inputs}: -> net {gate.output}: {output_state}')

            # Remove the ready gates from the list of gates yet to be processed
            gates_to_process.difference_update(ready_gates)

        # All nets have been evaluated. Save the output net state to return
        output_result = self.format_outputs()

        # Reset the net-list state so we can evaluate a new input vector later
        self.reset_state()

        return output_result

    def evaluate_gate_output(self, gate: Gate) -> Logic:
        """
        Using the current net-list state,
        evaluate what the output net state should be for the given gate.
        """
        # sanity check to ensure only valid gates get evaluated
        if not self.all_nets_assigned(gate.inputs):
            raise TypeError('Cannot evaluate a gate with unassigned inputs.')

        input_states = tuple(self._net_states[net_id] for net_id in gate.inputs)
        return gate.evaluate(*input_states)

    def find_ready_gates(self, gates: set[Gate]) -> set[Gate]:
        """Return all gates from `gates` with all input nets assigned"""

        ready_gates = set()
        for gate in gates:
            if self.all_nets_assigned(gate.inputs):
                ready_gates.add(gate)
        return ready_gates

    def reset_state(self):
        """Reset the net-list assignments, ready to evaluate a new input"""
        self._net_states = {net_id: Logic.UNASSIGNED for net_id in self._net_states}

    def all_nets_assigned(self, net_ids: Collection[int]) -> bool:
        """
        Return true if all given net ids are assigned a logic value.
        If collection is empty or none, check all known net's
        """
        if not net_ids:
            net_ids = self._net_states.keys()
        return all(self._net_states[id] != Logic.UNASSIGNED for id in net_ids)

    def validate_input_string(self, string: str) -> list[Logic]:
        """
        Check if the string contains only '0's and '1's,
        and matches the number of expected input nets
        """
        if not all(char in '01' for char in string):
            raise RuntimeError("Input string must contain only '0's and '1's.")

        if len(string) != len(self._inputs):
            raise RuntimeError(
                f'Input vector length must match the number of input nets ({len(self._inputs)})'
            )

        # Convert the string to a list of boolean values
        return [Logic(char == '1') for char in string]

    def format_outputs(self):
        """A string representation of the circuit output state."""
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
