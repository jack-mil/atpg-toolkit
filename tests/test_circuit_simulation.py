import unittest
from pathlib import Path

from simulator.simulator import Simulation


class TestCircuit(unittest.TestCase):
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

    def test_evaluate_input(self):
        for netlist_file, input_vector, expected_output in self.test_cases:
            with self.subTest(netlist=netlist_file, vector=input_vector):
                circuit = Simulation(Path(netlist_file))
                self.assertEqual(circuit.simulate_input(input_vector), expected_output)


if __name__ == '__main__':
    unittest.main(verbosity=2)
