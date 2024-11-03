import unittest
from dataclasses import FrozenInstanceError
from simulator.structs import Gate, GateType, Logic


class TestGate(unittest.TestCase):
    def test_gate_equality(self):
        gate1 = Gate(GateType.AND, (1, 2), 3)
        gate2 = Gate(GateType.AND, (1, 2), 3)
        gate3 = Gate(GateType.OR, (1, 2), 3)

        self.assertEqual(gate1, gate2)
        self.assertNotEqual(gate1, gate3)

    def test_gate_immutability(self):
        gate = Gate(GateType.AND, (1, 2), 3)

        with self.assertRaises(FrozenInstanceError):
            gate.output = 4

    def test_gate_evaluation(self):
        gate_inv = Gate(GateType.INV, (1,), 2)
        gate_buf = Gate(GateType.BUF, (1,), 2)
        gate_and = Gate(GateType.AND, (1, 0), 3)
        gate_or = Gate(GateType.OR, (1, 0), 4)
        gate_nor = Gate(GateType.NOR, (1, 0), 5)
        gate_nand = Gate(GateType.NAND, (1, 0), 6)
        
        self.assertEqual(gate_inv.evaluate(Logic.HIGH), Logic.LOW)
        self.assertEqual(gate_buf.evaluate(Logic.HIGH), Logic.HIGH)
        self.assertEqual(gate_and.evaluate(Logic.HIGH, Logic.LOW), Logic.LOW)
        self.assertEqual(gate_or.evaluate(Logic.HIGH, Logic.LOW), Logic.HIGH)
        self.assertEqual(gate_nor.evaluate(Logic.HIGH, Logic.LOW), Logic.LOW)
        self.assertEqual(gate_nand.evaluate(Logic.HIGH, Logic.LOW), Logic.HIGH)

    def test_invalid_gate_evaluation(self):
        gate = Gate(GateType.AND, (1, 2), 3)

        with self.assertRaises(TypeError):
            gate.evaluate(Logic(True))


if __name__ == '__main__':
    unittest.main()
