import unittest
from dataclasses import FrozenInstanceError
from simulator.structs import Gate, GateType, Logic


class TestGate(unittest.TestCase):
    def test_gate_equality(self):
        gate1 = Gate(GateType.And, (1, 2), 3)
        gate2 = Gate(GateType.And, (1, 2), 3)
        gate3 = Gate(GateType.Or, (1, 2), 3)

        self.assertEqual(gate1, gate2)
        self.assertNotEqual(gate1, gate3)

    def test_gate_immutability(self):
        gate = Gate(GateType.And, (1, 2), 3)

        with self.assertRaises(FrozenInstanceError):
            gate.output = 4 # type: ignore

    def test_gate_evaluation(self):
        gate_inv = Gate(GateType.Inv, (1,), 2)
        gate_buf = Gate(GateType.Buf, (1,), 2)
        gate_and = Gate(GateType.And, (1, 0), 3)
        gate_or = Gate(GateType.Or, (1, 0), 4)
        gate_nor = Gate(GateType.Nor, (1, 0), 5)
        gate_nand = Gate(GateType.Nand, (1, 0), 6)
        
        self.assertEqual(gate_inv.evaluate(Logic.High), Logic.Low)
        self.assertEqual(gate_buf.evaluate(Logic.High), Logic.High)
        self.assertEqual(gate_and.evaluate(Logic.High, Logic.Low), Logic.Low)
        self.assertEqual(gate_or.evaluate(Logic.High, Logic.Low), Logic.High)
        self.assertEqual(gate_nor.evaluate(Logic.High, Logic.Low), Logic.Low)
        self.assertEqual(gate_nand.evaluate(Logic.High, Logic.Low), Logic.High)

    def test_invalid_gate_evaluation(self):
        gate = Gate(GateType.And, (1, 2), 3)

        with self.assertRaises(TypeError):
            gate.evaluate(Logic(True))


if __name__ == '__main__':
    unittest.main(verbosity=2)
