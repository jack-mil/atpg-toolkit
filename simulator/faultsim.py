from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from .structs import Gate, Logic

from .simulator import Simulation
from .structs import Fault


class FaultSimulation(Simulation):
    """A circuit simulation that can determine stuck-at faults detected by test vectors"""

    def __init__(self, netlist: Path | str | list[str]):
        """
        Initialize a new fault simulation to simulate the circuit defined in `netlist`.

        Multiple tests can be simulated using the same FaultSimulation object.
        Optionally load from a list of strings in the format of net-list file lines (for testing)
        """
        # # initialize base simulation for fault-free execution
        super().__init__(netlist)

        self._fault_lists: dict[int, set[Fault]] = dict()
        """Mapping of all net ids (nodes) in the circuit and their fault list"""

    def detect_faults(self, test_vector: str) -> set[Fault]:
        """
        Return the set of all faults detected by a test vector.
        Faults are simulated on the circuit defined for this simulation.
        """
        # convert the input string to internal representation,
        vector = self.validate_input_string(test_vector)
        # and propagate input faults through the netlist
        self._deduce_faults(vector)

        # detected faults is the union of all fault lists on all output nets
        output_faults = set.union(
            *(self._fault_lists[output_net] for output_net in self.circuit.outputs), set()
        )
        # Reset the net-list state so we can evaluate a new input vector later
        self.reset()
        return output_faults

    def _deduce_faults(self, vector: list[Logic]):
        """
        Run a fault free simulation concurrently at the same time as propagating the faults.
        TODO: Some code is duplicated from Simulation, I would like to fix that
        """

        # Initialize the initial input net fault lists with their opposite stuck-at fault
        for net_id, state in zip(self.circuit.inputs, vector, strict=True):
            self._net_states[net_id] = state
            self._fault_lists[net_id] = {Fault(net_id, ~state)}

        gates_to_process = self.circuit.gates.copy()
        # Simulate until every gate has been evaluated and faults propagated
        while len(gates_to_process) > 0:
            ready_gates = self.find_ready_gates(gates_to_process)
            for gate in ready_gates:
                self._propagate_ready_gate(gate)

            # Remove the ready gates from the list of gates yet to be processed
            gates_to_process.difference_update(ready_gates)

    def _propagate_ready_gate(self, gate: Gate):
        """
        Using current fault-free net-list state and net fault lists,
        propagate all detected faults from gate inputs to the output,
        and evaluate & update the fault-free output.
        """
        # see docs/deductive_sim_fault_propagation.png for textbook equation used here
        input_states = tuple(self._net_states[net_id] for net_id in gate.inputs)

        control_value = gate.control_value()
        # Inverts and Buffers don't have a controlling value, and so this set is empty for them
        controlling_inputs = {
            net for net, state in zip(gate.inputs, input_states) if state is control_value
        }
        non_controlling_inputs = set(gate.inputs) - controlling_inputs

        # start by propagating all faults on non-controlling inputs
        propagated = set.union(*(self._fault_lists[net] for net in non_controlling_inputs), set())
        if len(controlling_inputs) > 0:
            # in case there are inputs at a controlling value,
            # only propagate faults that affect all inputs at a controlling value,
            # and don't affect the previous non-controlling input faults
            # (see textbook)
            exclusive_faults = set.intersection(
                *(self._fault_lists[net] for net in controlling_inputs)
            )
            propagated = exclusive_faults - propagated

        # evaluate the result of the gate inputs and update the net-list state
        output_state = gate.evaluate(*input_states)
        self._net_states[gate.output] = output_state

        # include the local output fault, and record the propagated faults
        propagated.add(Fault(gate.output, ~output_state))
        self._fault_lists[gate.output] = propagated

    def reset(self):
        super().reset()
        self._fault_lists = dict()
