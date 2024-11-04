from pathlib import Path
from itertools import chain
from .simulator import Simulation
from .structs import Fault, Logic, Gate, GateType


class FaultSimulation:
    def __init__(self, netlist: Path | list[str]):
        # initialize base simulation for fault-free execution
        self._sim = Simulation(netlist)

        self._fault_lists: dict[int, set[Fault]] = self.reset_state()
        """Mapping of all net ids (nodes) in the circuit and their fault list"""

    def detect_faults(self, test_vector: str) -> set[Fault]:
        """
        Find which faults are detected by a test vector.
        Faults are simulated on the circuit defined for this simulation.
        """
        vector = self._sim.validate_input_string(test_vector)

        # simulate fault free and propagate input faults through the netlist
        self._deduce_faults(vector)

        # detected faults is the union of all fault lists on all output nets
        output_faults = set(
            chain.from_iterable(
                self._fault_lists[output_net] for output_net in self._sim._circuit._outputs
            )
        )

        self._fault_lists = self.reset_state()
        self._sim._net_states = self._sim.reset_state()

        return output_faults

    def _deduce_faults(self, vector: list[Logic]):
        """"""

        # Initialize the input nets fault lists with their opposite stuck-at fault
        for net_id, state in zip(self._sim._circuit._inputs, vector, strict=True):
            self._sim._net_states[net_id] = state
            self._fault_lists[net_id].add(Fault(net_id, ~state))

        gates_to_process = self._sim._circuit._gates.copy()
        # simulate until every gate has been evaluated
        while len(gates_to_process) > 0:
            ready_gates = self._sim.find_ready_gates(gates_to_process)

            for gate in ready_gates:
                input_states = tuple(self._sim._net_states[net_id] for net_id in gate.inputs)
                output_state = gate.evaluate(*input_states)

                list_a = self._fault_lists[gate.inputs[0]]
                list_b = self._fault_lists[gate.inputs[1]]

                # all inputs are at controlling value
                if (input_states[0] is Logic.LOW) and (input_states[1] is Logic.LOW):
                    propagated = list_a & list_b
                # input a is controlling value, b isn't
                elif input_states[0] is Logic.LOW:
                    propagated = list_a - list_b
                # input b is controlling value, a isn't
                elif input_states[1] is Logic.LOW:
                    propagated = list_b - list_a
                # no inputs at controlling value
                else:
                    propagated = list_a | list_b

                # evaluate the result of the gate inputs and update the net-list state
                self._sim._net_states[gate.output] = output_state
                self._fault_lists[gate.output] = propagated | {Fault(gate.output, ~output_state)}

            # Remove the ready gates from the list of gates yet to be processed
            gates_to_process.difference_update(ready_gates)

    def reset_state(self) -> dict[int, set[Fault]]:
        return {net_id: set() for net_id in self._sim._circuit._nets}
