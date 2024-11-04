import unittest
from pathlib import Path

from simulator import Logic
from simulator import FaultSimulation
from simulator.structs import Fault


class TestDeductiveFaultSim(unittest.TestCase):

    def test_and_gate(self):
        """Test a simple circuit net-list made by hand"""
        netlist = [
            'AND 1 2 3',
            'INPUT 1 2 -1',
            'OUTPUT 3 -1',
        ]
        and_faults = {
            '11': {Fault(1, Logic.LOW), Fault(2, Logic.LOW), Fault(3, Logic.LOW)},
            '10': {Fault(3, Logic.HIGH), Fault(2, Logic.HIGH)},
            '01': {Fault(3, Logic.HIGH), Fault(1, Logic.HIGH)},
            '00': {Fault(3, Logic.HIGH)},
        }
        sim = FaultSimulation(netlist)

        for test, correct_faults in and_faults.items():
            with self.subTest(test=test):
                found_faults = sim.detect_faults(test)
                print(found_faults)
                self.assertEqual(found_faults, correct_faults)


if __name__ == '__main__':
    unittest.main(verbosity=2)
