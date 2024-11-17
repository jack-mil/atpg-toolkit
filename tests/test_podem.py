import unittest

from simulator import Fault, Logic

from podem import TestGenerator

class TestPodemUnits(unittest.TestCase):
    def test_backtrace(self):
        netlist = [ # example circuit from textbook Figure 6.28
            'INV a c',
            'NAND c b d',
            'INV d f',
            'INPUT a b -1',
            'OUTPUT f -1'
        ]
        podem = TestGenerator(netlist)

        objective = ('f', Logic.High) # output net 6 at logic '1'

        primary_in_net, value = podem.backtrace(*objective)
        print(f'{primary_in_net=}, {value=}')

        self.assertEqual(primary_in_net, 'a')
        self.assertEqual(value, Logic.Low)

        # need to imply() a=0 and run backtrace() again
        # should come up with b=1

