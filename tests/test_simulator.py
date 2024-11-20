import unittest
from pathlib import Path

from simulator.simulator import BaseSim, Simulation
from simulator.structs import Logic


class TestBaseSim(unittest.TestCase):
    def test_5state(self):
        """Test using the BaseSim forward simulation with D-Calculus"""
        netlist = [
            'INV 1 5',
            'NAND 2 3 6',
            'AND 5 2 7',
            'OR 6 4 8',
            'NAND 7 8 9',
            'INPUT 1 2 3 4 -1',
            'OUTPUT 9 8 -1',
        ]

        input_vector = [Logic.D, Logic.High, Logic.Low, Logic.X]
        expected_output = [Logic.D, Logic.High]

        sim = BaseSim(netlist)
        # using internal implementation
        sim._simulate_input(input_vector)
        outputs = sim.get_out_values()
        sim.reset()

        self.assertListEqual(outputs, expected_output)

        input_vector = [Logic.Dbar, Logic.High, Logic.High, Logic.X]
        expected_output = [Logic.X, Logic.X]

        sim._simulate_input(input_vector)
        outputs = sim.get_out_values()
        sim.reset()

        self.assertListEqual(outputs, expected_output)


class TestSimulator(unittest.TestCase):
    def setUp(self):
        # Nelist files and corresponding expected outputs for each input vector
        self.test_cases = [
            # (netlist file, input vector, expected output)
            ('circuits/s27.net', '1110101', '1001'),
            ('circuits/s27.net', '0001010', '0100'),
            ('circuits/s298f_2.net', '00101010101010101', '00000010101000111000'),
            ('circuits/s298f_2.net', '01011110000000111', '00000000011000001000'),
            ('circuits/s344f_2.net', '101010101010101011111111', '10101010101010101010101101'),
            ('circuits/s344f_2.net', '010111100000001110000000', '00011110000000100001111100'),
            ('circuits/s349f_2.net', '101010101010101011111111', '10101010101010101101010101'),
            ('circuits/s349f_2.net', '010111100000001110000000', '00011110000000101011110000'),
        ]

    def test_comprehensive(self):
        """Run a integration test for the matrix of netlists and input vectors against expected output strings"""
        for netlist_file, input_vector, expected_output in self.test_cases:
            with self.subTest(netlist=netlist_file, vector=input_vector):
                sim = Simulation(Path(netlist_file))
                output = sim.simulate_input(input_vector)
                self.assertEqual(output, expected_output)

    def test_simple_case(self):
        """Test a simple circuit net-list made by hand"""
        netlist = [
            'INV 1 4',
            'NAND 2 3 5',
            'OR 4 5 6',
            'INPUT 1 2 3 -1',
            'OUTPUT 5 6 -1',
        ]
        sim = Simulation(netlist)
        reset_state = dict()  # unset nets don't have a key in the dict
        # check proper init
        self.assertDictEqual(reset_state, sim._net_states)
        self.assertFalse(sim.all_nets_assigned())

        # check correct output
        self.assertEqual(sim.simulate_input('111'), '00')

        # check proper reset
        self.assertDictEqual(reset_state, sim._net_states)


if __name__ == '__main__':
    unittest.main(verbosity=2)
