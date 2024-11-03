from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING: 
    from pathlib import Path
    from typing import Collection, Self

from .structs import Gate, GateType


class Circuit:
    """
    A Circuit is a stateless definition of the logic gates and input/output nets
    associated with a particular combinational logic circuit.

    - The Circuit object does not hold any simulation state of nodes.
    - The Circuit is initialized from a net-list file in a particular format using `load_circuit_from_file()`"
    """

    def __init__(self):
        """
        Initialize a Circuit with default (empty) configuration.
          Use `Circuit.load_circuit_from_file(Path)` to initialize a specific net-list.
        """

        self._inputs: list[int] = list()
        """List of circuit input net ids (order matters)"""

        self._outputs: list[int] = list()
        """List of circuit output net ids (order matters)"""

        self._gates: set[Gate] = set()
        """Set of all logic Gates in this circuit"""

        self._nets: set[int] = set()
        """Set of all net id's (nodes) in this circuit"""

    @classmethod
    def load_circuit_from_file(cls, netlist_file: Path) -> Self:
        """
        Initialize and return a Circuit by reading from a net-list file.

        The file must have the format:
        ```
          # One or more lines of Gate definitions
          GATE_TYPE [1-2 input nets] [1 output net]
          INV 9 5
          NAND 16 17 14
          # The last two lines are special INPUT and OUTPUT net definitions
          INPUT  1 2 3 4 6 8 10 -1 # <- -1 end deliminator (REQUIRED)
          OUTPUT  7 9 11 5 -1
        ```
        """
        if not netlist_file.exists():
            raise RuntimeError(f'Net-list file "{netlist_file}" could not be found')

        with netlist_file.open() as f:
            # prefilter blank lines
            lines = [line.rstrip() for line in f if line]

        circuit = cls()

        for line in lines:  # process line
            keyword, *nets = line.split()  # split on whitespace
            nets = list(map(int, nets))  # map all net id's to numbers

            if keyword in GateType:
                # add each net id we encounter to the set. Some may repeat, that's ok
                circuit._nets.update(nets)
                # the last net id in the line is the gate output net
                *in_ids, out_id = nets
                # Create a new gate and add it to internal set
                circuit._gates.add(
                    Gate(GateType(keyword), output=out_id, inputs=tuple(in_ids)),
                )

            elif keyword == 'INPUT':
                *in_ids, _ = nets
                circuit._inputs.extend(circuit.ensure_nets_exist(in_ids))

            elif keyword == 'OUTPUT':
                *out_ids, _ = nets
                circuit._outputs.extend(circuit.ensure_nets_exist(out_ids))

            else:
                raise RuntimeError(f'Unknown gate type {keyword} in line: {line}')

        return circuit

    def ensure_nets_exist(self, net_ids: Collection[int]) -> Collection[int]:
        """Check to make sure that all given net_ids exist in this circuit."""
        missing_keys = set(net_ids).difference(self._nets)
        if missing_keys:
            raise RuntimeError(
                f'Undefined input net(s) encountered. Nets: "{missing_keys}" not found net-list'
            )
        return net_ids
