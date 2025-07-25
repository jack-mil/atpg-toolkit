import unittest
from dataclasses import FrozenInstanceError

import pytest

from atpg_toolkit.gates import Gate, GateType
from atpg_toolkit.logic import Logic
from atpg_toolkit.util import str_to_fault


class TestFaults(unittest.TestCase):
    def test_string_conversion(self):
        strings = [
            '1-sa-0',
            'a-sa-1',
            'net1-sa-0',
            '404-sa-1',
            'test 0',
            'a 0',
            '9\t0',
            '56        1',
        ]
        for fault in strings:
            success = str_to_fault(fault)
            self.assertIsNotNone(success)


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
            gate.output = 4  # pyright: ignore[reportAttributeAccessIssue]

    def test_gate_evaluation(self):
        inv = Gate(GateType.Inv, (1,), 2)
        buf = Gate(GateType.Buf, (1,), 2)
        and_gate = Gate(GateType.And, (1, 0), 3)
        or_gate = Gate(GateType.Or, (1, 0), 4)
        nor_gate = Gate(GateType.Nor, (1, 0), 5)
        nand_gate = Gate(GateType.Nand, (1, 0), 6)

        self.assertEqual(inv.evaluate(Logic.High), Logic.Low)
        self.assertEqual(buf.evaluate(Logic.High), Logic.High)
        self.assertEqual(and_gate.evaluate(Logic.High, Logic.Low), Logic.Low)
        self.assertEqual(or_gate.evaluate(Logic.High, Logic.Low), Logic.High)
        self.assertEqual(nor_gate.evaluate(Logic.High, Logic.Low), Logic.Low)
        self.assertEqual(nand_gate.evaluate(Logic.High, Logic.Low), Logic.High)

    def test_invalid_gate_evaluation(self):
        gate1 = Gate(GateType.And, (1, 2), 3)

        with self.assertRaises(TypeError):
            _ = gate1.evaluate(Logic.High)

        with pytest.raises(TypeError, match='Gate of type OR must have >= 2 inputs'):
            _ = Gate(GateType.Or, (2,), 3)

    def test_logic_xor(self):
        # only for literal High and Low values (for now)
        self.assertTrue((Logic.High ^ Logic.Low) is Logic.High)
        self.assertTrue((Logic.Low ^ Logic.Low) is Logic.Low)
        self.assertTrue((Logic.High ^ Logic.High) is Logic.Low)

        # should error
        with self.assertRaises(TypeError):
            _ = Logic.D ^ Logic.Low
        with self.assertRaises(TypeError):
            _ = Logic.High ^ Logic.X

    def test_dcalc_logic(self):
        # fmt: off

        # 5 state inversion
        self.assertTrue( ~ Logic.X    is Logic.X   )
        self.assertTrue( ~ Logic.D    is Logic.Dbar)
        self.assertTrue( ~ Logic.Dbar is Logic.D   )
        self.assertTrue( ~ Logic.High is Logic.Low )
        self.assertTrue( ~ Logic.Low  is Logic.High)

        # selection of 5-state AND logic
        self.assertTrue((Logic.High & Logic.X   ) is Logic.X    )
        self.assertTrue((Logic.High & Logic.D   ) is Logic.D    )
        self.assertTrue((Logic.High & Logic.Dbar) is Logic.Dbar )
        self.assertTrue((Logic.Low  & Logic.D   ) is Logic.Low  )
        self.assertTrue((Logic.X    & Logic.Low ) is Logic.Low  )
        self.assertTrue((Logic.D    & Logic.High) is Logic.D    )
        self.assertTrue((Logic.D    & Logic.D   ) is Logic.D    )
        self.assertTrue((Logic.Dbar & Logic.D   ) is Logic.Low  )
        self.assertTrue((Logic.Dbar & Logic.Dbar) is Logic.Dbar )

        with self.assertRaises(TypeError):
            _ = Logic.High & True
        with self.assertRaises(TypeError):
            _ = Logic.X    & 42
        with self.assertRaises(TypeError):
            _ = Logic.High & None

        # selection of 5-state OR logic
        self.assertTrue((Logic.High | Logic.X   ) is Logic.High )
        self.assertTrue((Logic.High | Logic.D   ) is Logic.High )
        self.assertTrue((Logic.High | Logic.Dbar) is Logic.High )
        self.assertTrue((Logic.X    | Logic.Low ) is Logic.X    )
        self.assertTrue((Logic.X    | Logic.D   ) is Logic.X    )
        self.assertTrue((Logic.X    | Logic.High) is Logic.High )
        self.assertTrue((Logic.Low  | Logic.D   ) is Logic.D    )
        self.assertTrue((Logic.Dbar | Logic.Low ) is Logic.Dbar )
        self.assertTrue((Logic.D    | Logic.Dbar) is Logic.High )
        self.assertTrue((Logic.D    | Logic.D   ) is Logic.D    )
        self.assertTrue((Logic.Dbar | Logic.Dbar) is Logic.Dbar )

        with self.assertRaises(TypeError):
            _ = Logic.D   | False
        with self.assertRaises(TypeError):
            _ = Logic.X   | 42
        with self.assertRaises(TypeError):
            _ = Logic.Low | None

        # fmt: on


if __name__ == '__main__':
    unittest.main(verbosity=2)
