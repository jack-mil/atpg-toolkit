#set text(lang: "en")
#import "template2.typ": *

#show: ilm.with(
  title: [Final Project Report],
  author: "Jackson Miller",

  table-of-contents: none,
  chapter-pagebreak: false,
  appendix: (
    enabled: true,
    body: [
      #include "appendix_a.typ"
      #pagebreak()
      #include "appendix_b.typ"
    ],
  )
  // header: "Jackson Miller - ECE 6140",
  // header: "Final Project Report  Jackson Miller - ECE 6140",
)

= Logic Simulator
The `LogicSimulator` class implements a forward logic simulation for combinational
circuits up of 2-input AND/NAND/OR/NOR and single-input buffers and inverters. Any
of the 5-state logic values 1/0/D/#overline([D])/X can be set on the circuit
inputs, and running the simulation produces the state of all circuit nets. This
result is stored in a Python dictionary mapping of net id (int or string) to the
net state (Logic value).

Using the library looks like this.
```py
from atpg_toolkit import FaultSimulator

netlist = 'circuits/s27.net'
inputs = '1110101'
sim = Simulation(netlist)
outputs = sim.simulate_input(inputs)

print(inputs)
```

A command line interface is also provided for all components.

= Deductive Fault Simulator

The deductive fault simulator builds off of the previous fault-free simulation technique. I improved and organized the
program architecture, and made use of automated unit testing.

Here is an example of using the `FaultSimulator` class, taken from `scripts/coverage`.

```py
from atpg_toolkit import FaultSimulator

netlist = 'circuits/s27.net'
vector = '1110101'
sim = FaultSimulation(netlist)
faults = sim.detect_faults(vector)

print(faults)
```

The deductive fault simulator propagates a fault list $L$ to output $Z$ according to the equations below.
$C$ is the set of gate inputs at the controlling value $c$.
$
  bold("if") C &= emptyset bold("then") L_Z = {limits(union)_(j in I)L_j} &union {Z "s-a-"(c xor i)} \
  bold("else") L_Z &= {limits(sect)_(j in C) L_j} - {limits(union)_(j in I-C) L_j} &union {Z "s-a-"(macron(c) xor i)} \
$

== Part (a)
Below is a summary of the results of detecting faults on the various given circuits. See Appendix B for the entire list
of faults detected by each test vector.

#figure(
  caption: [Fault simulation summary],
  table(
    columns: (auto, auto, auto),
    align: (left, left, center),
    table.header([*File*], [*Test*], [*\# Detected Faults*]),
    [s27], [1101101], [9],
    [s27], [0101001], [13],
    [s298f_2], [10101011110010101], [87],
    [s298f_2], [11101110101110111], [53],
    [s344f_2], [101010101010111101111111], [82],
    [s344f_2], [111010111010101010001100], [132],
    [s349f_2], [101000000010101011111111], [97],
    [s349f_2], [111111101010101010001111], [137],
  ),
)

#pagebreak()
== Random vector coverage tests

Each netlist was simulated with random vectors to calculate fault coverage

$ "coverage" = "found_faults" / N * 100% $

where $N$ is the total number of possible stuck-at faults in the circuit, $2 * "total_nets"$.

The table summarizes the findings over an average of 15 sets of random test vectors. Because of the nature of random
vectors, every trial is different.
#show table.cell: set text(10pt)
#figure(
  caption: [Coverage test summary],
  table(
    columns: 4,
    align: (left, center, center, center),
    table.header([*File*], [*Total \# Faults*], [*Tests for 75% coverage*], [*Tests for 90% coverage*]),
    [s27.net], [20], [7.9], [17.7],
    [s298f_2.net], [202], [18.1], [49.5],
    [s344f_2.net], [190], [9.1], [22.9],
    [s349f_2.net], [189], [9.4], [21.8],
  ),
)

#figure(image("coverage_plot.png", width: 80%), caption: [Plot of coverage for each circuit.])

= PODEM Test Pattern Generator

The final part of this project is the implementation of the Path Orientated
Decision Making (PODEM) test pattern generation algorithm [Goel and Rosales 1981].
This is implemented in the Python `TestGenerator` class, which provides methods of
loading a circuit and generating a valid combination of inputs that detect a given
single-stuck fault.
The generated test vector can than be directly fed back into the previous
deductive fault simulator to find all faults which are detected by that test.
This this way, a small set of tests can be generated that cover many faults in the
circuit.

Usage of the library looks like this:

```py
from atpg_toolkit import TestGenerator

netlist = 'circuits/s27.net'
podem = TestGenerator(netlist)
fault = Fault(16, stuck_at=0) # many ways to define a fault
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


== Sample Generated Tests

The following tests where generated by providing a netlist and file with desired
faults to the application command line interface like this:
```sh
$ ./atpg-toolkit generate circuits/s298f_2.net -f scripts/data/s298f_2-faults.txt
```
Due to the (highly probable) possibility of multiple valid tests existing for any
given fault, the output of the PODEM algorithm in this implemenation is not deterministic. Multiple searches for the same fault can produce different test vectors. The data reproduced below is just a sample output on one occurance.

#include "podem_data.typ"
