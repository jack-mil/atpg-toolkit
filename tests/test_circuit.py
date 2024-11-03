import unittest
from simulator.circuit import Circuit
from simulator.structs import Gate, GateType


class TestCircuit(unittest.TestCase):
    def test_load_circuit(self):
        netlist = [
            'INV 1 4',
            'NAND 2 3 5',
            'OR 4 5 6',
            'INPUT 1 2 3 -1',
            'OUTPUT 6 -1',
        ]
        circuit = Circuit.load_circuit_from_strings(netlist)

        gates = {
            Gate(GateType.INV, (1,), 4),
            Gate(GateType.NAND, (2, 3), 5),
            Gate(GateType.OR, (4, 5), 6),
        }
        self.assertEqual(gates, circuit._gates)
        self.assertEqual({1, 2, 3, 4, 5, 6}, circuit._nets)
        self.assertEqual([1, 2, 3], circuit._inputs)
        self.assertEqual([6], circuit._outputs)


if __name__ == '__main__':
    unittest.main()
