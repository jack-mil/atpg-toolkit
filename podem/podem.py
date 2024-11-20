from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from simulator.structs import Fault, Gate, NetId

from simulator.simulator import BaseSim
from simulator.structs import Gate, Logic


def filter_errors(vector: list[Logic]) -> str:
    """
    Convert a list of Logic values into a bitstring representation
    Replaces D or Dbar with their 1/0 non-errored counterparts
    """
    bitstring = ''.join(str(v) for v in vector)
    bitstring = bitstring.replace(str(Logic.Dbar), str(Logic.Low))
    bitstring = bitstring.replace(str(Logic.D), str(Logic.High))
    return bitstring


class ErrorSim(BaseSim):
    """TODO: docs"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fault: Fault = None

    def set_state(self, id: NetId, value: Logic):
        """Override BaseSim method to inject a D/Dbar if target fault is every activated"""
        new_val = value
        # (one of inputs) is target fault line
        if self.fault and id == self.fault.net_id:
            error = self.fault.stuck_at
            # inject the D/Dbar error if fault has been activated
            match value, error:
                case Logic.High, Logic.Low:
                    new_val = Logic.D
                case Logic.Low, Logic.High:
                    new_val = Logic.Dbar
                case _:
                    pass

        return super().set_state(id, new_val)

    def start_state(self, fault: Fault):
        """Set internal state ready to do simulations for PODEM"""
        self.fault = fault
        self.reset()
        # explicitly give X values to the all primary inputs
        # in order to do 5-valued forward simulation to completion
        for net_id in self.circuit.inputs:
            self.set_state(net_id, Logic.X)

    def simulate_input_assignment(self, pi_net: NetId, value: Logic):
        """
        Assign a single primary input the given logic value.
        Retains any previous input assignments, and reruns the entire forward simulation
        """
        if pi_net not in self.circuit.inputs:
            raise ValueError(f'Net {pi_net} is not a Primary Input (PI)')

        # save the previous input assignments before resetting internal assignments
        prev_inputs = self.get_in_values()
        self.reset()

        # (re)assign all old input values
        for id, old_val in zip(self.circuit.inputs, prev_inputs, strict=True):
            self.set_state(id, old_val)

        # overwrite with the new input assignment
        self.set_state(pi_net, value)

        # perform a full forward simulation to update state
        self._make_implications()

    def build_d_frontier(self) -> set[Gate]:
        """
        Return all gates that currently have unset (X) output,
        but one or more D/D̅ values on inputs.
        TODO: find better place to optimize this, instead of full loop over all gates every iteration
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

        self.output_to_gate = {gate.output: gate for gate in self.sim.circuit.gates}
        """Mapping of a particular net to the Gate driving it."""

    def generate_test(self, fault: Fault):
        """
        Generate a test that detects the given fault

        Return the string representation of the input assignments to detect the fault.
        Order of inputs will match the order of inputs in the netlist-under-test.

        Return None if the fault is undetectable.
        """
        # reset and prepare forward-simulation engine
        self.sim.start_state(fault)

        # recursively execute the PODEM algorithm
        success = self.podem(fault)
        if success:
            # succeeded, replace D/Dbar in inputs with 0/1 and return test as a string
            test_vector = filter_errors(self.sim.get_in_values())
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
        while net in self.output_to_gate:
            driving_gate = self.output_to_gate[net]
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
        if any(value is Logic.D or value is Logic.Dbar for value in self.sim.get_out_values()):
            return True

        # cannot determine success
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

        # cannot determine failure
        return False

    def pick_unset_input(self, gate: Gate) -> NetId:
        """Get an arbitrary net with unassigned value from `gate`"""
        net = next(input for input in gate.inputs if self.sim.get_state(input) is Logic.X)
        return net
