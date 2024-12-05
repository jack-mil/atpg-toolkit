from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .gates import Gate
    from .types import NetId, StrPath

from . import util
from .logic import Fault, Logic
from .simulator import BaseSim


class FaultSimulation(BaseSim):
    """A circuit simulation that can determine stuck-at faults detected by test vectors."""

    def __init__(self, netlist: StrPath | list[str]):
        """
        Initialize a new fault simulation to simulate the circuit defined in `netlist`.

        Multiple tests can be simulated using the same FaultSimulation object.

        Optionally load from a list of strings in the format of net-list file lines (for testing)
        """
        # # initialize base simulation for fault-free execution
        super().__init__(netlist)

        self._fault_lists: dict[NetId, set[Fault]] = dict()
        """Mapping of all net ids (nodes) in the circuit and their fault list"""

    def detect_faults(self, test_vector: str) -> set[Fault]:
        """
        Return the set of all faults detected by a given test vector.
        Faults are propagated through the circuit defined for this simulation.

        The input string must be a binary string e.g. "1X01XX0" with X's as don't care conditions
        The order of inputs will be matched to the order of inputs from the net-list definition.
        """
        # convert the input string to machine representation,
        vector = util.bitstring_to_logic(test_vector)

        # Initialize the initial input net fault lists with their opposite stuck-at fault
        for net_id, state in zip(self.circuit.inputs, vector):
            self._fault_lists[net_id] = set() if state is Logic.X else {Fault(net_id, ~state)}

        # and propagate input faults through the netlist
        self._simulate_input(vector)

        # detected faults is the union of all fault lists on all output nets
        output_faults = set.union(*(self._fault_lists[output_net] for output_net in self.circuit.outputs), set())
        # Reset the net-list state so we can evaluate a new input vector later
        self.reset()
        return output_faults

    def _process_ready_gate(self, gate: Gate) -> Logic:
        """
        Use current fault-free net-list state and fault lists to
        propagate all detected faults from gate inputs to the output,
        and evaluate & update the fault-free output.

        See docs/images/deductive_sim_fault_propagation.png for textbook equation used here

        Base class override, called by internal _simulate_input()
        """
        input_states = self.gate_input_values(gate)

        control_value = gate.control_value()
        # Inverts and Buffers don't have a controlling value, and so this set is empty for them
        controlling_inputs = {
            net for net, state in zip(gate.inputs, input_states, strict=True) if state is control_value
        }
        non_controlling_inputs = set(gate.inputs) - controlling_inputs

        # start by propagating all faults on non-controlling inputs
        propagated = set.union(*(self._fault_lists[net] for net in non_controlling_inputs), set())
        if len(controlling_inputs) > 0:
            # in case there are inputs at a controlling value,
            # only propagate faults that affect all inputs at a controlling value,
            # and don't affect the previous non-controlling input faults
            # (see textbook)
            exclusive_faults = set.intersection(*(self._fault_lists[net] for net in controlling_inputs))
            propagated = exclusive_faults - propagated

        # evaluate the result of the gate inputs
        output_state = super()._process_ready_gate(gate)

        # include the local output fault, and record the propagated faults
        if output_state is not Logic.X:
            propagated.add(Fault(gate.output, ~output_state))
        self._fault_lists[gate.output] = propagated

        # return output for use by BaseSim
        return output_state

    def reset(self):
        """Reset the base sim and the fault lists."""
        super().reset()
        self._fault_lists = dict()
