from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Collection
    from .structs import Gate

from .circuit import Circuit
from .structs import GateType, Logic, Fault


class Simulation:
    """
    The Simulation class keeps track of the current fault-free state of all the nets in the circuit.
    A Simulation object is loaded with a specific circuit definition from a net-list file.

    Given an input vector, use simulate_input(vector) to get the output of the simulated circuit
    """

    def __init__(self, netlist_file: Path | list[str]):
        """
        Initialize a new simulation object to simulate the circuit defined in `netlist_file`.

        Multiple input simulation vectors can be run with the same Simulation object.

        Optionally load from a list of strings in the format of netlist file lines (for testing)
        """

        self._circuit = (
            Circuit.load_circuit_from_strings(netlist_file)
            if isinstance(netlist_file, list)
            else Circuit.load_circuit_from_file(netlist_file)
        )
        """Static, state-less representation of the topology of the circuit (gates and net ids)"""

        self._net_states: dict[int, Logic] = self.reset_state()
        """Mapping of all net ids in the circuit, and the associated logic state (HIGH, LOW, UNASSIGNED)."""

    def simulate_input(self, input_str: str) -> str:
        """
        With a valid input vector, simulate the circuit completely,
        and return the resulting output vector.

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
        self._net_states = self.reset_state()

        return output_result

    def _run_simulation(self, vector: list[Logic]):
        """Internal implementation that does not reset the simulated state"""

        # Initialize the input nets with the input vector values
        for net_id, state in zip(self._circuit._inputs, vector, strict=True):
            self._net_states[net_id] = state

        gates_to_process = self._circuit._gates.copy()
        # simulate until every gate has been evaluated
        while len(gates_to_process) > 0:
            ready_gates = self.find_ready_gates(gates_to_process)

            for gate in ready_gates:
                output_state = self.evaluate_gate_output(gate)
                # evaluate the result of the gate inputs and update the net-list state
                self._net_states[gate.output] = output_state

            # Remove the ready gates from the list of gates yet to be processed
            gates_to_process.difference_update(ready_gates)

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

    def all_nets_assigned(self, net_ids: None | Collection[int] = None) -> bool:
        """
        Return true if all given net ids are assigned a logic value.
        If collection is empty or none, check all known net's
        """
        if net_ids is None:
            net_ids = self._net_states.keys()
        return all(self._net_states[id] != Logic.UNASSIGNED for id in net_ids)

    def reset_state(self) -> dict[int, Logic]:
        """Return a dictionary with all circuit nets (nodes) in uninitialized state."""
        return {net_id: Logic.UNASSIGNED for net_id in self._circuit._nets}

    def validate_input_string(self, string: str) -> list[Logic]:
        """
        Check if the string contains only '0's and '1's,
        and matches the number of expected input nets.

        Return the input vector string as a list of Logic values
        """
        if not all(char in '01' for char in string):
            raise RuntimeError("Input string must contain only '0's and '1's.")

        if len(string) != len(self._circuit._inputs):
            raise RuntimeError(
                f'Input vector length must match the number of input nets ({len(self._circuit._inputs)})'
            )

        # Convert the string to a list of boolean values
        return [Logic(char == '1') for char in string]

    def format_outputs(self) -> str:
        """A string representation of the circuit output state."""
        output_str = ''
        for net_id in self._circuit._outputs:
            match self._net_states[net_id]:
                case Logic.HIGH:
                    output_str += '1'
                case Logic.LOW:
                    output_str += '0'
                case Logic.UNASSIGNED:
                    output_str += '?'
        return output_str
