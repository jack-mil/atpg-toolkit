import unittest
from pathlib import Path

from atpg_toolkit import Fault, FaultSimulation, Gate, GateType, Logic, TestGenerator


class TestPodemUnits(unittest.TestCase):
    def test_backtrace(self):
        netlist = [  # example circuit from textbook Figure 6.28
            'INV a c',
            'NAND c b d',
            'INV d f',
            'INPUT a b -1',
            'OUTPUT f -1',
        ]
        objective = ('f', Logic.High)  # try to set net f to logic '1'

        podem = TestGenerator(netlist)
        pi_net, value = podem.backtrace(*objective)
        print(f'{pi_net=}, {value=}')

        self.assertEqual(pi_net, 'a')
        self.assertEqual(value, Logic.Low)

        # manually make implications
        podem.sim._net_states['a'] = Logic.Low
        podem.sim._net_states['c'] = Logic.High

        # assigning just a=0 does not achieve objective
        # try again
        pi_net, value = podem.backtrace(*objective)
        print(f'{pi_net=}, {value=}')
        # should come up with b=1
        self.assertEqual(pi_net, 'b')
        self.assertEqual(value, Logic.High)

    def test_objective_simple(self):
        netlist = [  # example circuit from textbook Figure 6.28
            'INV a c',
            'NAND c b d',
            'INV d f',
            'INPUT a b -1',
            'OUTPUT f -1',
        ]
        target_fault = Fault('f', Logic.Low)

        podem = TestGenerator(netlist)
        net, value = podem.objective(target_fault)

        # first time should pick opposite of fault
        self.assertEqual(net, 'f')
        self.assertEqual(value, Logic.High)

        net, value = podem.objective(target_fault)

    def test_objective_two_steps(self):
        netlist = [  # example circuit from textbook Figure 6.28
            'INV a d',
            'AND b d e',
            'NOR e c f',
            'INPUT a b c -1',
            'OUTPUT f -1',
        ]
        target_fault = Fault('b', Logic.Low)

        podem = TestGenerator(netlist)

        # manually set state for next objective
        podem.sim._net_states['e'] = Logic.X
        podem.sim._net_states['d'] = Logic.X
        podem.sim._net_states['b'] = Logic.D
        podem.d_frontier = {Gate(GateType.And, ('b', 'd'), 'e')}

        net, value = podem.objective(target_fault)
        # next objective should try to propagate error to net 'e'
        self.assertEqual(net, 'd')
        self.assertEqual(value, Logic.High)

        # continues until D reaches primary output

    def test_imply(self):
        netlist = [  # example circuit from textbook Figure 6.28
            'INV a c',
            'NAND c b d',
            'INV d f',
            'INPUT a b -1',
            'OUTPUT f -1',
        ]
        podem = TestGenerator(netlist)

        pi_assignement = ('a', Logic.Low)
        podem.imply(*pi_assignement)

        self.assertEqual(podem.sim.get_state('a'), Logic.Low)
        self.assertEqual(podem.sim.get_state('c'), Logic.High)
        self.assertEqual(podem.sim.get_state('b'), Logic.X)
        self.assertEqual(podem.sim.get_state('d'), Logic.X)

        # next input assignment builds on last
        pi_assignement = ('b', Logic.High)
        podem.imply(*pi_assignement)

        self.assertEqual(podem.sim.get_state('a'), Logic.Low)
        self.assertEqual(podem.sim.get_state('c'), Logic.High)
        self.assertEqual(podem.sim.get_state('b'), Logic.High)
        self.assertEqual(podem.sim.get_state('d'), Logic.Low)
        self.assertEqual(podem.sim.get_state('f'), Logic.High)


class TestSimplePodem(unittest.TestCase):
    def test_and_gate(self):
        """Generate a test vector for a single AND gate."""
        netlist = [
            'AND 1 2 3',
            'INPUT 1 2 -1',
            'OUTPUT 3 -1',
        ]
        tests_for_faults = {
            Fault(3, Logic.High): {'0X', 'X0'},
            Fault(3, Logic.Low): {'11'},
            Fault(1, Logic.Low): {'11'},
            Fault(2, Logic.Low): {'11'},
            Fault(1, Logic.High): {'01'},
            Fault(2, Logic.High): {'10'},
        }

        podem = TestGenerator(netlist)

        for fault, expected_tests in tests_for_faults.items():
            with self.subTest(msg=str(fault)):
                found_test = podem.generate_test(fault)
                self.assertIn(found_test, expected_tests)

    def test_small_circuit(self):
        netlist = [
            'NAND B C E',
            'NAND A E F',
            'NAND C E G',
            'NAND D E I',
            'NAND F G H',
            'INPUT A B C D -1',
            'OUTPUT H I -1',
        ]
        fault_tests = {
            Fault('G', 0): {'X111', ...},  # probably more, idk
            Fault('B', 0): {'X111', ...},  # probably more, idk
            Fault('I', 0): {'X111', 'XXX0', ...},  # probably more, idk
            Fault('E', 1): {'X111', ...},
            Fault('H', 0): {'10XX', ...},
        }
        podem = TestGenerator(netlist)
        sim = FaultSimulation(netlist)
        for target_fault, expected_tests in fault_tests.items():
            with self.subTest(msg=str(target_fault)):
                found_test = podem.generate_test(target_fault)
                # unreliable because I don't have every test that detects given fault
                # self.assertIn(found_test, expected_tests)
                if found_test is not None:
                    detected_faults = sim.detect_faults(found_test)
                    self.assertIn(target_fault, detected_faults)

    def test_undetectable_faults(self):
        netlist = [
            'BUF a d',
            'BUF a e',
            'NAND b d f',
            'OR c f g',
            'AND g e i',
            'INPUT a b c -1',
            'OUTPUT i -1',
        ]

        podem = TestGenerator(netlist)
        all_faults = podem.sim.circuit.all_faults()
        results = {str(fault): podem.generate_test(fault) for fault in all_faults}
        self.assertIsNone(results['d-sa-1'])

        from atpg_toolkit.podem import InvalidNetError
        from atpg_toolkit.util import str_to_fault

        with self.assertRaises(InvalidNetError):
            podem.generate_test(str_to_fault('404-sa-0'))

    @unittest.skip('Requires multi-input gate support')
    def test_circuit_hand(self):
        """Test the circuit and fault from Textbook Figure 6.24 (see docs/)."""
        netlist = [
            'NAND a b c g',
            "INV d d'",
            "INV e e'",
            "INV f f'",
            "NAND a d' h",
            'NAND d g i',
            "NAND b e' j",
            'NAND e g k',
            "NAND c f' l",
            'NAND f g m',
            'NOR h i j k l m n',
            'INPUT a b c d e f -1',
            'OUTPUT n -1',
        ]

        fault = Fault('a', stuck_at=1)
        expected_test = '011111'

        podem = TestGenerator(netlist)

        found_test = podem.generate_test(fault)

        self.assertEqual(found_test, expected_test)


class TestPodemComplete(unittest.TestCase):
    def setUp(self):
        # Nelist files and corresponding expected outputs for each input vector
        self.test_cases = [
            # (netlist file, target fault, expected test)
            ('circuits/s27.net', Fault(16, 0), 'X0X10X0'),
            ('circuits/s27.net', Fault(18, 1), '11X101X'),
            ('circuits/s298f_2.net', Fault(70, 1), '01X1XXXXXXXXXX0XX'),
            ('circuits/s298f_2.net', Fault(92, 0), 'X10101XXXXXX0X0XX'),
            ('circuits/s344f_2.net', Fault(166, 0), '01X00XXXXX011XX0XXXXXXXX'),
            ('circuits/s344f_2.net', Fault(91, 1), '111XXXXXXXXXXXXXXXXXXXXX'),
            ('circuits/s349f_2.net', Fault(25, 1), 'XXXXXXXXXXXXXXX1XXXXXXXX'),
            ('circuits/s349f_2.net', Fault(7, 0), 'XXXXXX1XXXXXXXXXXXXXXXXX'),
        ]

    def test_comprehensive(self):
        """
        Run a integration test for the matrix of netlists and target faults against
        the detected faults from feeding the test into the simulator.
        """
        for netlist_file, target_fault, expected_test in self.test_cases:
            _, _, stub = netlist_file.partition('/')
            with self.subTest(msg=f'{stub} : {target_fault}'):
                atpg = TestGenerator(Path(netlist_file))
                test = atpg.generate_test(target_fault)

                self.assertIsNotNone(test)

                sim = FaultSimulation(Path(netlist_file))
                detected_faults = sim.detect_faults(test)

                self.assertIn(target_fault, detected_faults)

                # exact match will sometimes work, sometimes not,
                # because of arbitrary path selection and multiple
                # correct tests to detect a single fault
                # with self.subTest(msg='Exact match'):
                #     self.assertEqual(test, expected_test)
