import unittest

from podem import TestGenerator
from simulator.structs import Fault, Gate, GateType, Logic


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
        """Generate a test vector for a single AND gate"""
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
            with self.subTest(test=str(fault)):
                found_test = podem.generate_test(fault)
                self.assertIn(found_test, expected_tests)
