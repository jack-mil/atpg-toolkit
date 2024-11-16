import unittest

from simulator import Fault, FaultSimulation, Logic


class TestFaultsSingleGates(unittest.TestCase):
    def test_and_gate(self):
        """Test a single AND gate"""
        netlist = [
            'AND 1 2 3',
            'INPUT 1 2 -1',
            'OUTPUT 3 -1',
        ]
        and_faults = {
            '00': {Fault(3, Logic.High)},
            '01': {Fault(3, Logic.High), Fault(1, Logic.High)},
            '10': {Fault(3, Logic.High), Fault(2, Logic.High)},
            '11': {Fault(1, Logic.Low), Fault(2, Logic.Low), Fault(3, Logic.Low)},
        }
        sim = FaultSimulation(netlist)

        for test, correct_faults in and_faults.items():
            with self.subTest(test=test):
                found_faults = sim.detect_faults(test)
                print(found_faults)
                self.assertSetEqual(found_faults, correct_faults)

    def test_or_gate(self):
        """Test a single OR gate"""
        netlist = [
            'OR 1 2 3',
            'INPUT 1 2 -1',
            'OUTPUT 3 -1',
        ]
        or_faults = {
            '00': {Fault(1, Logic.High), Fault(2, Logic.High), Fault(3, Logic.High)},
            '01': {Fault(3, Logic.Low), Fault(2, Logic.Low)},
            '10': {Fault(3, Logic.Low), Fault(1, Logic.Low)},
            '11': {Fault(3, Logic.Low)},
        }
        sim = FaultSimulation(netlist)

        for test, correct_faults in or_faults.items():
            with self.subTest(test=test):
                found_faults = sim.detect_faults(test)
                print(found_faults)
                self.assertSetEqual(found_faults, correct_faults)

    def test_nor_gate(self):
        """Test a single NOR gate"""
        netlist = [
            'NOR 1 2 3',
            'INPUT 1 2 -1',
            'OUTPUT 3 -1',
        ]
        nor_faults = {
            '00': {Fault(1, Logic.High), Fault(2, Logic.High), Fault(3, Logic.Low)},
            '01': {Fault(2, Logic.Low), Fault(3, Logic.High)},
            '10': {Fault(1, Logic.Low), Fault(3, Logic.High)},
            '11': {Fault(3, Logic.High)},
        }
        sim = FaultSimulation(netlist)

        for test, correct_faults in nor_faults.items():
            with self.subTest(test=test):
                found_faults = sim.detect_faults(test)
                print(found_faults)
                self.assertSetEqual(found_faults, correct_faults)

    def test_nand_gate(self):
        """Test a single NAND gate"""
        netlist = [
            'NAND 1 2 3',
            'INPUT 1 2 -1',
            'OUTPUT 3 -1',
        ]
        nand_faults = {
            '00': {Fault(3, Logic.Low)},
            '01': {Fault(3, Logic.Low), Fault(1, Logic.High)},
            '10': {Fault(3, Logic.Low), Fault(2, Logic.High)},
            '11': {Fault(1, Logic.Low), Fault(2, Logic.Low), Fault(3, Logic.High)},
        }
        sim = FaultSimulation(netlist)

        for test, correct_faults in nand_faults.items():
            with self.subTest(test=test):
                found_faults = sim.detect_faults(test)
                print(found_faults)
                self.assertSetEqual(found_faults, correct_faults)

    def test_inverter(self):
        """Test a single inverter"""
        netlist = [
            'INV 1 2',
            'INPUT 1 -1',
            'OUTPUT 2 -1',
        ]
        inv_faults = {
            '0': {Fault(1, Logic.High), Fault(2, Logic.Low)},
            '1': {Fault(1, Logic.Low), Fault(2, Logic.High)},
        }
        sim = FaultSimulation(netlist)

        for test, correct_faults in inv_faults.items():
            with self.subTest(test=test):
                found_faults = sim.detect_faults(test)
                self.assertSetEqual(found_faults, correct_faults)


class TestFaultSimulator(unittest.TestCase):
    def test_small_netlist(self):
        """Find all faults in small circuit and check exact output"""
        expected_faults = {
            Fault(1, Logic.Low),
            Fault(3, Logic.Low),
            Fault(5, Logic.Low),
            Fault(7, Logic.Low),
            Fault(9, Logic.High),
            Fault(11, Logic.High),
            Fault(12, Logic.Low),
            Fault(13, Logic.Low),
        }
        netlist = 'circuits/s27.net'
        vector = '1110101'
        sim = FaultSimulation(netlist)
        faults = sim.detect_faults(vector)
        self.assertSetEqual(faults, expected_faults)

    def test_can_do_regular_sim(self):
        """Ensure that the FaultSimulation class preserves functionality of parent class"""
        netlist = [
            'INV 1 4',
            'NAND 2 3 5',
            'OR 4 5 6',
            'INPUT 1 2 3 -1',
            'OUTPUT 5 6 -1',
        ]
        sim = FaultSimulation(netlist)
        reset_state = {
            1: Logic.X,
            2: Logic.X,
            3: Logic.X,
            4: Logic.X,
            5: Logic.X,
            6: Logic.X,
        }
        # check correct initial state
        self.assertDictEqual(reset_state, sim._net_states)
        self.assertFalse(sim.all_nets_assigned())

        # check correct output
        self.assertEqual(sim.simulate_input('111'), '00')

        # check proper reset
        self.assertDictEqual(reset_state, sim._net_states)
        self.assertDictEqual(dict(), sim._fault_lists)


if __name__ == '__main__':
    unittest.main(verbosity=2)
