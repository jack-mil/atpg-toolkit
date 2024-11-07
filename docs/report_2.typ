#set page(paper: "us-letter", margin: (top: 0.5in, bottom: 0.5in, x: 0.5in, y: 0.5in))
#show figure.where(kind: table): set figure.caption(position: top)
#show table.cell: set text(10pt)

= Deductive Fault Simulator Report
- Jackson Miller
- 11/8/2024
- ECE 6140


The deductive fault simulator builds off of the previous fault-free simulation technique. I improved and organized the
program architecture, and made use of automated unit testing.

Here is an example of using the FaultSimulator class, taken from `scripts/coverage`.

```py
from simulator import FaultSimulator

netlist = 'circuits/s27.net'
vector = '1110101'
sim = FaultSimulation(netlist)
faults = sim.detect_faults(vector)

print(faults)
```

== Part (a)
Below is a summary of the results of detecting faults on the various given circuits. See Appendix A for the entire list
of faults detected by each test vector.



#figure(
  caption: [Fault simulation summary],
  table(
    columns: (auto, auto, auto),
    align: (left, left, center),
    fill: (_, y) => if calc.odd(y) {
      rgb("EAF2F5")
    },
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
== Part (b)

Each netlist was simulated with random vectors to calculate fault coverage

$
  "coverage" = "found_faults" / N * 100%
$

where $N$ is the total number of possible stuck-at faults in the circuit, $2 * "total_nets"$.

The table summarizes the findings over an average of 15 sets of random test vectors. Because of the nature of random
vectors, every trial is different.
#figure(
  caption: [Coverage test summary],
  table(
    columns: 4,
    align: (left, center, center, center),
    fill: (_, y) => if calc.odd(y) {
      rgb("EAF2F5")
    },
    table.header([*File*], [*Total \# Faults*], [*Tests for 75% coverage*], [*Tests for 90% coverage*]),
    [s27.net], [20], [7.9], [17.7],
    [s298f_2.net], [202], [18.1], [49.5],
    [s344f_2.net], [190], [9.1], [22.9],
    [s349f_2.net], [189], [9.4], [21.8],
  ),
)

#figure(image("coverage_plot.png", width: 80%), caption: [Plot of coverage for each circuit.])

#pagebreak()

== Appendix A

#include "appendix.typ"
