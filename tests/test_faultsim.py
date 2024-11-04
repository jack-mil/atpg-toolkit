import unittest
from pathlib import Path

from simulator import Logic
from simulator import FaultSimulation
from simulator.structs import Fault


class TestFaultsSingleGates(unittest.TestCase):
    def test_and_gate(self):
        """Test a single AND gate"""
        netlist = [
            'AND 1 2 3',
            'INPUT 1 2 -1',
            'OUTPUT 3 -1',
        ]
        and_faults = {
            '00': {Fault(3, Logic.HIGH)},
            '01': {Fault(3, Logic.HIGH), Fault(1, Logic.HIGH)},
            '10': {Fault(3, Logic.HIGH), Fault(2, Logic.HIGH)},
            '11': {Fault(1, Logic.LOW), Fault(2, Logic.LOW), Fault(3, Logic.LOW)},
        }
        sim = FaultSimulation(netlist)

        for test, correct_faults in and_faults.items():
            with self.subTest(test=test):
                found_faults = sim.detect_faults(test)
                print(found_faults)
                self.assertEqual(found_faults, correct_faults)

    def test_or_gate(self):
        """Test a single OR gate"""
        netlist = [
            'OR 1 2 3',
            'INPUT 1 2 -1',
            'OUTPUT 3 -1',
        ]
        or_faults = {
            '00': {Fault(1, Logic.HIGH), Fault(2, Logic.HIGH), Fault(3, Logic.HIGH)},
            '01': {Fault(3, Logic.LOW), Fault(2, Logic.LOW)},
            '10': {Fault(3, Logic.LOW), Fault(1, Logic.LOW)},
            '11': {Fault(3, Logic.LOW)},
        }
        sim = FaultSimulation(netlist)

        for test, correct_faults in or_faults.items():
            with self.subTest(test=test):
                found_faults = sim.detect_faults(test)
                print(found_faults)
                self.assertEqual(found_faults, correct_faults)

    def test_nor_gate(self):
        """Test a single NOR gate"""
        netlist = [
            'NOR 1 2 3',
            'INPUT 1 2 -1',
            'OUTPUT 3 -1',
        ]
        nor_faults = {
            '00': {Fault(1, Logic.HIGH), Fault(2, Logic.HIGH), Fault(3, Logic.LOW)},
            '01': {Fault(2, Logic.LOW), Fault(3, Logic.HIGH)},
            '10': {Fault(1, Logic.LOW), Fault(3, Logic.HIGH)},
            '11': {Fault(3, Logic.HIGH)},
        }
        sim = FaultSimulation(netlist)

        for test, correct_faults in nor_faults.items():
            with self.subTest(test=test):
                found_faults = sim.detect_faults(test)
                print(found_faults)
                self.assertEqual(found_faults, correct_faults)

    def test_nand_gate(self):
        """Test a single NAND gate"""
        netlist = [
            'NAND 1 2 3',
            'INPUT 1 2 -1',
            'OUTPUT 3 -1',
        ]
        nand_faults = {
            '00': {Fault(3, Logic.LOW)},
            '01': {Fault(3, Logic.LOW), Fault(1, Logic.HIGH)},
            '10': {Fault(3, Logic.LOW), Fault(2, Logic.HIGH)},
            '11': {Fault(1, Logic.LOW), Fault(2, Logic.LOW), Fault(3, Logic.HIGH)},
        }
        sim = FaultSimulation(netlist)

        for test, correct_faults in nand_faults.items():
            with self.subTest(test=test):
                found_faults = sim.detect_faults(test)
                print(found_faults)
                self.assertEqual(found_faults, correct_faults)

    def test_inverter(self):
        """Test a single inverter"""
        netlist = [
            'INV 1 2',
            'INPUT 1 -1',
            'OUTPUT 2 -1',
        ]
        inv_faults = {
            '0': {Fault(1, Logic.HIGH), Fault(2, Logic.LOW)},
            '1': {Fault(1, Logic.LOW), Fault(2, Logic.HIGH)},
        }
        sim = FaultSimulation(netlist)

        for test, correct_faults in inv_faults.items():
            with self.subTest(test=test):
                found_faults = sim.detect_faults(test)
                print(found_faults)
                self.assertEqual(found_faults, correct_faults)

if __name__ == '__main__':
    unittest.main(verbosity=2)
