import unittest

from atpg_toolkit import Circuit, Gate
from atpg_toolkit.gates import GateType
from atpg_toolkit.types import NetlistFormatError


class TestCircuit(unittest.TestCase):
    def test_load_circuit(self):
        """Test loading a simple circuit."""
        netlist = [
            'INV 1 4',
            'NAND 2 3 5',
            'OR 4 5 6',
            'INPUT 1 2 3 -1',
            'OUTPUT 6 -1',
        ]
        circuit = Circuit.load_strings(netlist)

        gates = {
            Gate(GateType.Inv, (1,), 4),
            Gate(GateType.Nand, (2, 3), 5),
            Gate(GateType.Or, (4, 5), 6),
        }
        self.assertSetEqual(gates, circuit.gates)
        self.assertSetEqual({1, 2, 3, 4, 5, 6}, circuit.nets)
        self.assertListEqual([1, 2, 3], circuit.inputs)
        self.assertListEqual([6], circuit.outputs)

    def test_load_circuit_str_nets(self):
        """Test the generic net naming support (combination str and int)."""
        netlist = [
            'INV a 2',
            'AND b 2 3',
            'NAND c 2 5',
            'OR 5 3 7',
            'NOR 7 6 out',
            'INPUT a b c -1',
            'OUTPUT out -1',
        ]
        circuit = Circuit.load_strings(netlist)

        gates = {
            Gate(GateType.Inv, ('a',), 2),
            Gate(GateType.And, ('b', 2), 3),
            Gate(GateType.Nand, ('c', 2), 5),
            Gate(GateType.Or, (5, 3), 7),
            Gate(GateType.Nor, (7, 6), 'out'),
        }
        self.assertSetEqual(gates, circuit.gates)
        self.assertSetEqual({'a', 'b', 'c', 'out', 2, 3, 5, 6, 7}, circuit.nets)
        self.assertListEqual(['a', 'b', 'c'], circuit.inputs)
        self.assertListEqual(['out'], circuit.outputs)

    def test_unknown_gate(self):
        """Test handling invalid gate type."""
        unknown_gate = [
            'BAR 1 2 3',  # <-
            'INPUT 1 2  -1',
            'OUTPUT 3 -1',
        ]
        with self.assertRaises(NetlistFormatError) as cm:
            _ = Circuit.load_strings(unknown_gate)
        print(cm.exception)

    def test_undefined_io_nets(self):
        """Test handling undefined nets."""
        unknown_gate = [
            'AND 1 2 3',
            'OR 3 4 5',
            'INPUT 10 11  -1',  # <- 10 11 don't exist
            'OUTPUT 3 -1',
        ]
        with self.assertRaises(NetlistFormatError) as cm:
            _ = Circuit.load_strings(unknown_gate)
        print(cm.exception)

    def test_conflicting_io(self):
        """Test handling conflicting input/output nets."""
        inputs_are_gate_outputs = [
            'AND 1 2 3',
            'OR 4 5 6',
            'INPUT 1 2 6 -1',  # <- net 6 is output of OR gate
            'OUTPUT 3 -1',
        ]
        with self.assertRaises(NetlistFormatError) as cm:
            _ = Circuit.load_strings(inputs_are_gate_outputs)
        print(cm.exception)

        pi_in_po = [
            'AND 1 2 3',
            'OR 3 2 6',
            'INPUT 1 2 -1',
            'OUTPUT 1 6 -1',  # <- net 1 is both input and output. weird but allowed
        ]
        circuit = Circuit.load_strings(pi_in_po)
        self.assertListEqual([1, 2], circuit.inputs)
        self.assertListEqual([1, 6], circuit.outputs)

        # no_input = [
        #     'AND 1 2 3',
        #     'OUTPUT 3 -1',
        # ]
        # with self.assertRaises(NetlistFormatError) as cm:
        #     _ = Circuit.load_strings(no_input)
        # print(cm.exception)

    def test_bad_gate(self):
        """Test gate with missing inputs."""
        bad_gate_nets = [
            'AND 1 3',  # <- invalid one-input AND gate
            'INPUT 1 -1',
            'OUTPUT 3 -1',
        ]
        with self.assertRaises(NetlistFormatError) as cm:
            _ = Circuit.load_strings(bad_gate_nets)
        print(cm.exception)

    def test_bad_delimiter(self):
        """Test handling missing INPUT delimiter."""
        missing_end = [
            'AND 1 2 3',
            'INPUT 1 2',  # <- missing -1
            'OUTPUT 3 -1',
        ]
        with self.assertRaises(NetlistFormatError) as cm:
            _ = Circuit.load_strings(missing_end)
        print(cm.exception)

    def test_multiple_drivers(self):
        """Test handling multiple output drivers."""
        conflicting_gate_outputs = [
            'AND 1 2 4',  # <-
            'NAND 2 3 4',  # <-
            'INPUT 1 2 3 -1',
            'OUTPUT 4 -1',
        ]
        with self.assertRaises(NetlistFormatError) as cm:
            _ = Circuit.load_strings(conflicting_gate_outputs)
        print(cm.exception)


if __name__ == '__main__':
    unittest.main(verbosity=2)
