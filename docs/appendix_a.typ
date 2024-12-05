// #show raw:set text(size:11pt)

= User Manual: ATPG Toolkit

ATPG Toolkit is a pure Python implementation of a 5-valued logic circuit simulator, deductive fault simulator, and the PODEM test pattern generation technique.

The project repository is available at #link("https://github.com/jack-mil/atpg-toolkit").

The only requirement for running is Python version *3.13*. The code has been testing on both Windows and Linux.

In the source distribution, you will find an importable Python package called `atpg_toolkit`. This package provides an API to perform fault analysis on a netlist. Also provided is the `atpg_toolkit._cli` subpackage, intended to provide a command line interface for simple functions. The command line interface should be invoked by running the python module as a script: `python3 -m atpg_toolkit --help`.
For convenience, an executable script exists in the project root at `atpg-toolkit`, which can be run directly to get access to the CLI.

The Python library is fully type-hinted and contains docstring comments that will display documentation in your editor (e.g. VSCode). For detailed usage of the library API, see some of the examples in the README file (on Github), or any of the unit-test cases.

Here is a high-level overview of the package contents
- `atpg_toolkit.gates.Gate`
  - Representation of a logic gate of a certain type ((N)AND/(N)OR/INV/BUF)
  - Gates implement an `.evaluate()` method that performs the correct operation based in it's type (5-valued logic is further abstracted into the `Logic` enum).

- `atpg_toolkit.circuit.Circuit`
  - Class to hold the static (stateless) representation of a circuit (`Nets` and `Gates`). Also provides methods for parsing netlist in various formats.
  - All of the Simulation and Generation classes have a `Circuit` member to navigate the netlist

- `atpg_toolkit.simulation.Simulation`
  - Fault free input vector simulation with the `Simulation.simulate_input()` method.
  - The `BaseSim` parent provides the basis for general 5-valued simulation.

- `atpg_toolkit.faultsim.FaultSimulator`
  - Perform deductive fault simulation by propagating fault-lists through a circuit to detected faults given a test vector with `FaultSimulator.detect_faults()`.

- `atpg_toolkit.podem.TestGenerator`
  - The PODEM Test Pattern generator. Use `TestGenerator.generate_test()` to find a test for a fault.

#v(2em)

In the source distribution, you will also find several other folders related to development and testing. Many serve as useful reference of using the tools provided by the package.

- `circuits/`
  - netlists of various size that can be loaded by the Simulators
- `scripts/`
  - utility scripts (in Python and Bash) for generating the data in this report.
- `data/`
  - raw results from running the test cases in the `generate-results` script. This data was included in the report.
- `tests/`
  - a full Python unit-test suite used during development. Most classes and methods are tested, as well as some of the internal implementation. These tests were run automatically using Visual Studio Code's Python `unittest` integration.
- `docs/`
  - source code and images for this report (generated with #link("https://github.com/typst/typst")[Typst]).

== User Manual: Deductive Fault Simulator

Ensure Python *3.13* installed and accessible on PATH as `python` and/or `python3`.
Use a terminal to navigate to the root directory of the source distribution, or open the folder in a editor like VS Code.

To use the interactive command line interface, execute the python module using this command in a shell like Bash or Powershell.

`$ python -m atpg_toolkit --help`

The command line interface is split into 3 subcommands, `simulate`, `faults`, & `generate`.

To print all the stuck-at faults detected by the test vector `1 1 1 0 1 0 1` for the circuit in file `circuits/s27.net`, execute this command:

`$ python -m atpg_toolkit faults circuits/s27.net 1110101`

You should get this output:
#block(breakable: false)[
  //   #show raw: set text(size: 10pt)
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
]

Use `$ python -m atpg_toolkit faults --help` to see all options, including `-f <file` for reading a list of many input vectors from a file.


== User Manual: PODEM

PODEM operation is included in the `generate` subcommand of the CLI interface.

To print a test vector for each of the stuck-at faults 6-sa-1 and 10-sa-1
on the circuit in file `circuits/s27.net`, execute this command:

```
$ python -m atpg_toolkit generate circuits/s27.net 6-sa-1 10-sa-1

Circuit: circuits/s27.net
Fault   | Test
6-sa-1  | X0X10X0
10-sa-1 | 100XXX0
```

The `generate` subcommand also accepts the `-f <file>` flag to provide a file of many faults to generate tests for.
