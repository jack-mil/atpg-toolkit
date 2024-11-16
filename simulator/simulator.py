from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Collection
    from .structs import Gate

from .circuit import Circuit
from .structs import Logic


class Simulation:
    """
    The Simulation class can do a forward 5-state simulation of all nets in a circuit.
    A Simulation object is loaded with a specific circuit definition from a net-list file.

    Given an input vector, use simulate_input(vector) to get the output net states.
    Internally, inputs can be any of the Logic states (HIGH, LOW, D, D̅, X), and
    the D-Calculus is handled correctly.
    """

    def __init__(self, netlist: Path | str | list[str]):
        """
        Initialize a new simulation to simulate the circuit defined in `netlist`.

        Multiple input vectors can be simulated from the same Simulation object.
        Optionally load from a list of strings in the format of net-list file lines (for testing)
        """

        self.circuit = (
            Circuit.load_strings(netlist)
            if isinstance(netlist, list)
            else Circuit.load_file(netlist)
        )
        """Static, state-less representation of the topology of the circuit (gates and net ids)"""

        # self._net_states = {net_id: Logic.X for net_id in self.circuit.nets}
        self._net_states: dict[int, Logic] = dict()
        """Mapping of all net ids (nodes) in the circuit, and the associated Logic value (HIGH, LOW, D, D̅, X)."""

    def simulate_input(self, input_str: str) -> str:
        """
        Given an input vector string, simulate the fault-free circuit
        and return the resulting output vector string.

        The input string must be a binary string e.g. "1001010".
        The order of inputs will be matched to the order of inputs from the net-list definition.
        """

        # convert the input string to internal representation,
        vector = self.validate_input_string(input_str)
        # and run the simulation to final state
        self._run_simulation(vector)

        # All nets have been evaluated. Save the output state to return
        output_result = self.format_outputs()

        # Reset the net-list state so we can evaluate a new input vector later
        self.reset()
        return output_result

    def _run_simulation(self, vector: list[Logic]):
        """Internal implementation that does not reset the simulated state"""

        # Initialize the input nets with the input vector values
        for net_id, state in zip(self.circuit.inputs, vector, strict=True):
            self._net_states[net_id] = state

        gates_to_process = self.circuit.gates.copy()
        # Simulate until every gate has been evaluated
        while len(gates_to_process) > 0:
            ready_gates = self.find_ready_gates(gates_to_process)
            for gate in ready_gates:
                self._eval_ready_gate(gate)

            # Remove the ready gates from the list of gates yet to be processed
            gates_to_process.difference_update(ready_gates)

    def _eval_ready_gate(self, gate: Gate):
        """
        Using the current net-list state,
        evaluate what the output net state should be for the given gate.
        """

        # sanity check to ensure only valid gates get evaluated
        if not self.all_nets_assigned(gate.inputs):
            raise TypeError('Cannot evaluate a gate with unassigned inputs.')

        # evaluate the result of the gate inputs and update the net-list state
        input_states = tuple(self._net_states[net_id] for net_id in gate.inputs)
        output_state = gate.evaluate(*input_states)
        self._net_states[gate.output] = output_state

    def find_ready_gates(self, gates: set[Gate]) -> set[Gate]:
        """Return all gates from `gates` with all input nets assigned"""

        ready_gates = {gate for gate in gates if self.all_nets_assigned(gate.inputs)}
        return ready_gates

    def all_nets_assigned(self, net_ids: None | Collection[int] = None) -> bool:
        """
        Return true if all given net ids are assigned a logic value.
        If collection is empty or none, check all known net's
        """

        if net_ids is None:
            net_ids = self.circuit.nets  # all nets
        # net id's missing from the mapping are not assigned yet.
        return all(id in self._net_states for id in net_ids)

    def validate_input_string(self, string: str) -> list[Logic]:
        """
        Check if the string contains only '0's and '1's,
        and matches the number of expected input nets.

        Return the input vector string as a list of Logic values
        """

        if not all(char in '01' for char in string):
            raise RuntimeError("Input string must contain only '0's and '1's.")

        if len(string) != len(self.circuit.inputs):
            raise RuntimeError(
                f'Input vector length must match the number of input nets ({len(self.circuit.inputs)})'
            )

        # Convert the string to a list of boolean values
        # Logic.High and Logic.Low can be constructed from '1' and '0' respectively
        return [Logic(char) for char in string]

    def get_output_states(self) -> list[Logic]:
        """List of circuit output values in the order of original net-list"""
        return [self._net_states.get(net, Logic.X) for net in self.circuit.outputs]

    def format_outputs(self) -> str:
        """A string representation of the fault-free circuit output state."""
        output_str = ''
        for state in self.get_output_states():
            output_str += str(state)
        return output_str

    def reset(self):
        """Reset the simulation to all circuit nets (nodes) in uninitialized state."""
        self._net_states.clear()
