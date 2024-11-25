from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .structs import Gate
    from .types import NetId, StrPath

from . import util
from .circuit import Circuit
from .structs import Logic


class BaseSim:
    """
    The BaseSim class can do a forward 5-state simulation of all nets in a circuit.
    Used by fault free Simulation, deductive fault simulator, and PODEM implication routines.

    A BaseSim object is loaded with a specific circuit definition from a net-list file.

    Internally, inputs can be any of the Logic states (HIGH, LOW, D, D̅, X), and
    the D-Calculus is handled correctly.

    Subclasses should implement _process_ready_gate()
    to control what happens at each step in the simulation
    """

    def __init__(self, netlist: StrPath | list[str]):
        """
        Initialize a new simulation to simulate the circuit defined in `netlist`.

        Multiple input vectors can be simulated from the same Simulation object.
        Optionally load from a list of strings in the format of net-list file lines (for testing)
        """

        self.circuit = Circuit.load_strings(netlist) if isinstance(netlist, list) else Circuit.load_file(netlist)
        """Static, state-less representation of the topology of the circuit (gates and net ids)"""

        self._net_states: dict[NetId, Logic] = dict()
        """Mapping of all net ids (nodes) in the circuit, and the associated Logic value (HIGH, LOW, D, D̅, X)."""

    def _simulate_input(self, vector: list[Logic]):
        """
        Perform a forward simulation with the given primary input assignments.
        Does not return, only updates internal state of the nets.
        """

        if len(vector) != len(self.circuit.inputs):
            raise ValueError(f'Input vector length must match the number of input nets ({len(self.circuit.inputs)})')

        # Initialize the input nets with the input vector values
        for net_id, state in zip(self.circuit.inputs, vector, strict=True):
            self._net_states[net_id] = state

        self._make_implications()

    def _make_implications(self):
        """
        Do a forward simulation of any gates whose output can be determined by 5-valued D-Calculus
        This method alone is used by PODEM to simulate by incrementally making primary input assignments.
        """
        gates_to_process = self.circuit.gates.copy()
        # Simulate until every gate has been evaluated
        while len(gates_to_process) > 0:
            ready_gates = self.find_ready_gates(gates_to_process)
            for gate in ready_gates:
                new_state = self._process_ready_gate(gate)
                self.set_state(gate.output, new_state)

            # Remove the ready gates from the list of gates yet to be processed
            gates_to_process.difference_update(ready_gates)

    def _process_ready_gate(self, gate: Gate, *args, **kwargs) -> Logic:
        """
        Process a gate that has all inputs assigned, and return the output value.

        Override in derived classes to do extra functionality when each node is processed
        """
        # evaluate the result of the gate inputs and update the net-list state
        input_states = self.gate_input_values(gate)
        output_state = gate.evaluate(*input_states)
        return output_state

    def gate_input_values(self, gate: Gate) -> tuple[Logic, ...]:
        """Return the net values for all inputs of this `gate`."""
        input_values = tuple(self.get_state(id) for id in gate.inputs)
        return input_values

    def find_ready_gates(self, gates: set[Gate]) -> set[Gate]:
        """Return all gates from `gates` with all input nets assigned."""
        ready_gates = {gate for gate in gates if self.all_nets_assigned(gate.inputs)}
        return ready_gates

    def all_nets_assigned(self, net_ids: Iterable[NetId] | None = None) -> bool:
        """
        Return true if all given net ids are assigned a logic value.
        If collection is empty or none, check all known net's.
        """

        if net_ids is None:
            net_ids = self.circuit.nets  # all nets
        # net id's missing from the mapping are not assigned yet.
        return all(id in self._net_states for id in net_ids)

    def get_state(self, id: NetId) -> Logic:
        """Return the value of the net with `id` at this step in the simulation."""
        # if the net id doesn't exist in the mapping,
        # it has not been assigned (yet)
        return self._net_states.get(id, Logic.X)

    def set_state(self, id: NetId, value: Logic):
        """Assign logic `value` to net with `id`."""
        self._net_states[id] = value

    def get_out_values(self) -> list[Logic]:
        """List of circuit output values in the order of original net-list."""
        return [self.get_state(net) for net in self.circuit.outputs]

    def get_in_values(self) -> list[Logic]:
        """List of circuit input values in the order of original net-list."""
        return [self.get_state(net) for net in self.circuit.inputs]

    def reset(self):
        """Reset the simulation by setting all nets (nodes) uninitialized."""
        self._net_states.clear()


class Simulation(BaseSim):
    """
    The Simulation class is for fault-free simulation of a logic circuit
    using fully defined input values (1 or 0).

    Simulation provides `simulate_input(test_vector)` to perform a full
    simulation and return the string representation of the primary outputs
    """

    def simulate_input(self, input_str: str) -> str:
        """
        Given an input vector string, simulate the fault-free circuit
        and return the resulting output vector string.

        The input string must be a binary string e.g. "1001010".
        The order of inputs will be matched to the order of inputs from the net-list definition.
        """

        # convert the input string to machine representation
        vector = util.bitstring_to_logic(input_str)

        # and run the simulation to final state
        self._simulate_input(vector)

        # All nets have been evaluated. Save the output state to return
        output_result = util.logic_to_bitstring(self.get_out_values())

        # Reset the net-list state so we can evaluate a new input vector later
        self.reset()
        return output_result

    def _process_ready_gate(self, gate: Gate) -> Logic:
        """
        Use the current net-list state to evaluate what the
        fault-free output net value should be for the given gate.

        Extends BaseSim per-gate processing with error checking.
        """
        # sanity check to ensure only valid gates get evaluated
        if not self.all_nets_assigned(gate.inputs):
            raise ValueError('Cannot evaluate a gate with unassigned inputs.')

        return super()._process_ready_gate(gate)
