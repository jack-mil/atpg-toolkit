from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Literal

    from simulator.structs import Fault, NetId

from simulator.structs import Logic
from simulator.circuit import Circuit
from simulator.simulator import Simulation


class TestGenerator:
    """
    Use the PODEM (Path-Oriented Decision Making) Automatic Test Pattern Generation algorithm
    to generate test vectors for specific stuck-at faults on a given net-list of combinational logic gates.

    The class uses the same Circuit and Simulation primitives as the fault simulator.
    """

    def __init__(self, netlist: Path | str | list[str]):
        """
        Initialize a new test generator for the circuit in file `netlist`.

        Tests can be generated for multiple faults using the same TestGenerator object.

        Optionally, load from a list of strings in the format of net-list file lines (for testing)
        """

        self.sim = Simulation(netlist)
        """Static, state-less representation of the topology of the circuit (gates and net ids)"""

        self.gate_output_nets = {gate.output: gate for gate in self.sim.circuit.gates}
        """Mapping of a particular net to the Gate driving it."""

    def generate_tests(self, fault: Fault):
        return set()

    def backtrace(self, net: NetId, state: Literal[Logic.Low, Logic.High]):
        """
        Find a primary input (PI) assignment that is likely to contribute to
        setting the objective net (`net`) to a Logic High or Low (`state`).

        Returns a (net_id, state) pair where net_id is guaranteed be a primary input
        """

        # Follow an x-path from the target net until reaching a primary input
        # A net is considered a primary input if it is not driven by a gate output
        while net in self.gate_output_nets:
            driving_gate = self.gate_output_nets[net]
            # keep track of the inversion parity of the path
            state = state ^ driving_gate.inversion()
            # choose the first gate input with unassigned value (x-path)
            net = next(
                input for input in driving_gate.inputs if self.sim.get_net_state(input) is Logic.X
            )
            # loop

        # net_id is a primary input
        assert net in self.sim.circuit.inputs
        return net, state
