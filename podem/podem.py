from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from simulator.structs import Fault, Gate, NetId

from simulator.simulator import BaseSim
from simulator.structs import Gate, Logic


class ErrorSim(BaseSim):
    """TODO: docs"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fault: Fault = None

    def _process_ready_gate(self, gate: Gate) -> Logic:
        """TODO: docs"""
        output_state = super()._process_ready_gate(gate)

        # skip if no target set
        if self.fault is None:
            return output_state
        # inject the error state on the target net
        if gate.output == self.fault.net_id:
            if output_state is Logic.High and self.fault.stuck_at is Logic.Low:
                output_state = Logic.D
            elif output_state is Logic.Low and self.fault.stuck_at is Logic.High:
                output_state = Logic.Dbar
        return output_state

    def start_state(self, fault: Fault):
        """Set internal state ready to do simulations for PODEM"""
        self.fault = fault
        self.reset()
        # explicitly give X values to the all primary inputs
        # in order to do 5-valued forward simulation to completion
        for net_id in self.circuit.inputs:
            self._net_states[net_id] = Logic.X

    def get_input_states(self) -> list[Logic]:
        """List of circuit input values in the order of original net-list"""
        inputs = [self.get_state(net) for net in self.circuit.inputs]

        return inputs

    def format_inputs(self) -> str:
        """A string representation of the circuit input assignments"""
        inputs = self.get_input_states()
        inputs = [Logic.High if v is Logic.D else v for v in inputs]
        inputs = [Logic.Low if v is Logic.Dbar else v for v in inputs]
        input_str = ''.join(str(v) for v in inputs)
        
        return input_str

    def simulate_input_assignment(self, pi_net: NetId, value: Logic):
        """Assign a single primary input the given logic value."""
        if pi_net not in self.circuit.inputs:
            raise ValueError(f'Net {pi_net} is not a Primary Input (PI)')

        # save the previous input assignments before resetting internal assignments
        prev_inputs = self.get_input_states()
        self.reset()
        # assign old input values
        for net_id, state in zip(self.circuit.inputs, prev_inputs, strict=True):
            self._net_states[net_id] = state
        # overwrite with the new input assignment
        if self.fault and pi_net == self.fault.net_id:
            self._net_states[pi_net] = Logic.D if self.fault.stuck_at is Logic.Low else Logic.Dbar
        else:
            self._net_states[pi_net] = value
        # perform a full forward simulation to update state
        self._make_implications()

    def build_d_frontier(self) -> set[Gate]:
        """
        Return all gates that currently have unset (X) output,
        but one or more D/D̅ values on inputs.
        """
        d_frontier = set()
        for gate in self.circuit.gates:
            out_value = self.get_state(gate.output)
            if out_value is Logic.X:
                in_values = (self.get_state(net) for net in gate.inputs)
                if any(val is Logic.D or val is Logic.Dbar for val in in_values):
                    d_frontier.add(gate)
        return d_frontier


class TestGenerator:
    """
    Use the PODEM (Path-Oriented Decision Making)
    Automatic Test Pattern Generation algorithm
    to generate test vectors for specific stuck-at faults
    on a given net-list of combinational logic gates.

    The class uses the same Circuit and Simulation primitives as the fault simulator.
    """

    def __init__(self, netlist: Path | str | list[str]):
        """
        Initialize a new test generator for the circuit in file `netlist`.

        Tests can be generated for multiple faults using the same TestGenerator object.
        Optionally, load from a list of strings in the format of net-list file lines (for testing)
        """

        self.sim = ErrorSim(netlist)
        """TODO: add docs"""

        self.d_frontier: set[Gate] = set()
        """Gates whose output is unset (X) and at-least one input is D or D̅"""

        # TODO: rename
        self.gate_output_nets = {gate.output: gate for gate in self.sim.circuit.gates}
        """Mapping of a particular net to the Gate driving it."""

    def generate_test(self, fault: Fault):
        # reset and prepare forward-simulation engine
        self.sim.start_state(fault)

        # recursively execute the PODEM algorithm
        if self.podem(fault):
            # succeeded, return test as a string
            test_vector = self.sim.format_inputs()
            return test_vector

        # undetectable fault
        return None

    def podem(self, fault: Fault) -> bool:
        """Very literal Textbook PODEM algorithm with no optimization."""
        if self.check_success():
            return True

        if self.check_failure(fault):
            return False

        net, value = self.objective(fault)
        pi_net, value = self.backtrace(net, value)  # produces a Primary Input assignment

        self.imply(pi_net, value)  # forward simulate
        if self.podem(fault):  # recurse and try again
            return True

        self.imply(pi_net, ~value)  # reverse decision
        if self.podem(fault):  # recurse and try again
            return True

        # reset implication, path exhausted
        self.imply(pi_net, Logic.X)
        return False

    def imply(self, pi_net: NetId, value: Logic):
        # first simulate
        self.sim.simulate_input_assignment(pi_net, value)

        # maintain D frontier after each input simulation
        self.d_frontier = self.sim.build_d_frontier()

    def objective(self, target_fault: Fault):
        """
        Produce a net id and objective state for the target fault.

        First the target fault is activated; then resulting error is
        propagated towards a primary output (pg. 204).
        """

        # activate the target fault with opposite value
        if self.sim.get_state(target_fault.net_id) is Logic.X:
            return target_fault.net_id, ~target_fault.stuck_at

        # pick a gate from d-frontier
        gate = next(iter(self.d_frontier))
        # pick an unassigned input of the gate (x-path)
        net = self.pick_unset_input(gate)
        control_value = gate.control_value()
        assert control_value is not None  # Inv/Buf should never be in the d-frontier
        # objective is opposite of the controlling value
        # in order to propagate error on other gate input(s)
        return net, ~control_value

    def backtrace(self, net: NetId, state: Logic):
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
            # pick an unassigned input of the gate (x-path)
            net = self.pick_unset_input(driving_gate)
        # loop

        # net_id is a primary input
        assert net in self.sim.circuit.inputs
        return net, state

    def check_success(self) -> bool:
        """Return True if the fault has been detected"""
        # succeed if a primary output has a D or D̅
        if any(value is Logic.D or value is Logic.Dbar for value in self.sim.get_output_states()):
            return True

        # cannot determine
        return False

    def check_failure(self, fault: Fault) -> bool:
        """Return True if detecting the fault is impossible"""
        # faulty net cannot be activate
        if self.sim.get_state(fault.net_id) is fault.stuck_at:
            return True

        # D-frontier is empty, fault cannot be propagated
        if self.sim.get_state(fault.net_id) is not Logic.X and len(self.d_frontier) == 0:
            return True

        # Error propagation look-ahead (x-path check)
        # TODO: maybe in future implementation

        # might be detectible
        return False

    def pick_unset_input(self, gate: Gate) -> NetId:
        """Get an arbitrary net with unassigned value from `gate`"""
        net = next(input for input in gate.inputs if self.sim.get_state(input) is Logic.X)
        return net
