import unittest

from simulator import Circuit, Gate
from simulator.structs import GateType


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
            Gate(GateType.Inv, (1,), 4),
            Gate(GateType.Nand, (2, 3), 5),
            Gate(GateType.Or, (4, 5), 6),
        }
        self.assertSetEqual(gates, circuit._gates)
        self.assertSetEqual({1, 2, 3, 4, 5, 6}, circuit._nets)
        self.assertListEqual([1, 2, 3], circuit._inputs)
        self.assertListEqual([6], circuit._outputs)


if __name__ == '__main__':
    unittest.main(verbosity=2)
