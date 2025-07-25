import unittest

from atpg_toolkit import Fault, FaultSimulation, Logic


class TestFaultsSingleGates(unittest.TestCase):
    def test_and_gate(self):
        """Test a single AND gate."""
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
            with self.subTest(msg=test):
                found_faults = sim.detect_faults(test)
                print(found_faults)
                self.assertSetEqual(found_faults, correct_faults)

    def test_or_gate(self):
        """Test a single OR gate."""
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
            with self.subTest(msg=test):
                found_faults = sim.detect_faults(test)
                print(found_faults)
                self.assertSetEqual(found_faults, correct_faults)

    def test_nor_gate(self):
        """Test a single NOR gate."""
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
            with self.subTest(msg=test):
                found_faults = sim.detect_faults(test)
                print(found_faults)
                self.assertSetEqual(found_faults, correct_faults)

    def test_nand_gate(self):
        """Test a single NAND gate."""
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
            with self.subTest(msg=test):
                found_faults = sim.detect_faults(test)
                print(found_faults)
                self.assertSetEqual(found_faults, correct_faults)

    def test_inverter(self):
        """Test a single inverter."""
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
            with self.subTest(msg=test):
                found_faults = sim.detect_faults(test)
                self.assertSetEqual(found_faults, correct_faults)


class TestFaultSimulator(unittest.TestCase):
    def test_x_inputs(self):
        """
        Test detecting faults with X inputs.
        Circuit from Textbook Figure 6.58(a).
        """
        netlist = [
            'NAND B C E',
            'NAND A E F',
            'NAND C E G',
            'NAND D E I',
            'NAND F G H',
            'INPUT A B C D -1',
            'OUTPUT H I -1',
        ]
        wild_faults = {
            'X111': {Fault('E', 1)},
            '10XX': {Fault('H', 0)},
        }
        sim = FaultSimulation(netlist)

        for test, expected_faults in wild_faults.items():
            with self.subTest(msg=test):
                found_faults = sim.detect_faults(test)
                print(f'{test=}')
                print(*(f for f in found_faults))
                self.assertLessEqual(expected_faults, found_faults)

    def test_small_netlist(self):
        """Find all faults in small circuit and check exact output."""
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

    @unittest.skip('Requires XOR support')
    def test_xor_simulation(self):
        """Test deductive simulation on a circuit with input fanout."""
        netlist = [
            'NAND a b e',
            'NOR b c f',
            'AND d f g',
            'XOR e g h',
            'INPUT a b c d -1',
            'OUTPUT h -1',
        ]
        expected_faults = {
            Fault('e', Logic.High),
            # TODO: might be others, need to manually check
        }
        vector = '0XX0'
        sim = FaultSimulation(netlist)
        faults = sim.detect_faults(vector)
        self.assertSetEqual(faults, expected_faults)


if __name__ == '__main__':
    unittest.main(verbosity=2)
