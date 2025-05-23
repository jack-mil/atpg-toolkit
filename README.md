# Automatic Test Pattern Generation toolkit

Provides fault-free circuit simulation, deductive fault simulation, and PODEM test pattern generation for the single-stuck fault model in one extensible and self-contained Python library.

**External Dependencies**: None! Only Python 3.13 required.

Implements the 5-valued "D-Calculus" logic simulation (0,1,D,D̅,X).
- 0 : Logic low
- 1 : Logic high
- X : net with unknown/no logic level
- D : faulty net at 0 instead of 1
- D̅ : faulty net at 1 instead of 0


## Limitations
- Only 2-input AND/OR/NAND/NOR and 1-input inverters & buffers are supported
- No XOR gates
- The `Circuit` class can be extended to support parsing netlists in other, more standard formats.

The groundwork is here, I would like to revisit and add these features one day™

## Library Usage
```py
from atpg_toolkit import TestGenerator, FaultSimulation, Fault
from atpg_toolkit.util import str_to_fault

netlist = [ 'NAND A B E',
            'AND C E F',
            'OR D E out2',
            'NOR A E out1',
            'INPUT A B C D -1',
            'OUTPUT out1 out2 -1'   ]
# netlist can be a file or a list of gates
# net names can be letters/numbers/words
podem = TestGenerator(netlist)
fault = Fault('out1', stuck_at=1)
# fault = Fault('E', '1')
# fault = str_to_fault('E-sa-1')
# fault = str_to_fault('E 1')

found_test = podem.generate_test(fault)
print(found_test)

sim = FaultSimulation(netlist)

# produces set of faults detected by a test
faults = sim.detect_faults(found_test)
print(*faults)
```
See tests and the cli implementation for more examples

## CLI Usage
The primary usage of ATPG Toolkit is as a library for other python scripts.
However, a basic command-line utility is available for demonstration purposes, or to combine with output from other processes (see `scripts/` for examples).

When installed as a package, you can execute `python -m atpg_toolkit` to see the CLI usage. A entry point is also installed, and available as `atpg-toolkit`.

For more convenience as a tool, the `./atpg-toolkit` script can act as an executable entry-point on systems with script Shebang support. No installation of the package is necessary (but recommended).

```
$ python -m atpg_toolkit faults --help
usage: __main__.py [-h] [-v] {faults,f,generate,g,simulate,s} ...

Generate test patterns or simulate faults on digital logic circuits.

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit

Actions:
  {faults,f,generate,g,simulate,s}
    faults (f)          Find detected faults with a given net-list and test vector(s)      
    generate (g)        Find a test vector that detects a given fault
    simulate (s)        Perform fault-free simulation with a given net-list and test       
                        vector(s)

Copyright 2024, jack-mil. Source: https://github.com/jack-mil/atpg-toolkit
```

You can install the package with a tool like uv or pipx to make the tool available at the user level.

### Examples:
```
$ atpg_toolkit generate circuits/s349f_2.net 85-sa-1 10-sa-0 179-sa-1

Circuit: circuits/s349f_2.net
Fault    | Test
10-sa-0  | XXXXXXXXX1XXXXXXXXXXXXXX
85-sa-1  | 01X01XXXXX1XXXX0XXXXXXXX
179-sa-1 | UNDETECTABLE
```
```
$ python -m atpg_toolkit faults circuits/s27.net 1110101

Circuit: circuits/s27.net
Input Vector: 1 1 1 0 1 0 1
------ Detected Faults (8) ------
   1 stuck at 0
   3 stuck at 0
   5 stuck at 0
   7 stuck at 0
   9 stuck at 1
  11 stuck at 1
  12 stuck at 0
  13 stuck at 0
```
```
$ python -m atpg_toolkit simulate circuits/s27.net -f scripts/data/s27-tests.txt

Circuit: circuits/s27.net
Inputs  | Outputs
1110101 | 1001
0001010 | 0100
1010101 | 1001
0110111 | 0001
1010001 | 1001
```
## Disclaimer
> *This project implements textbook concepts for a course on digital 
> systems test generation. It is not recommended for any critical or 
> serious test generation needs. The code serves as reference and a 
> learning aid **only**. There is no guarantee of efficient operation
> or correct output.*

## Reference

> Miron Abramovici, M. A. Breuer, and A. D. Friedman, *Digital Systems Testing and Testable Design*. Wiley-IEEE Press, 1994.

> P. Goel and B. C. Rosales, "PODEM-X: An Automatic Test Generation System for VLSI Logic Structures," Proc. 18th Design Automation conf., pp. 260-268, June, 1981.
