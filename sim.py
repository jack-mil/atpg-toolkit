from pathlib import Path
from enum import StrEnum, Enum, auto
from dataclasses import dataclass


class GateType(StrEnum):
    INV = 'INV'
    BUF = 'BUF'
    AND = 'AND'
    OR = 'OR'
    NOR = 'NOR'
    NAND = 'NAND'

    def __repr__(self):
        return f'<{self.name}>'


class Logic(Enum):
    HIGH = True
    LOW = False
    UNASSIGNED = None

    def __repr__(self):
        return f'<Logic.{self.name}>'


@dataclass(eq=True, frozen=True)
class Gate:
    type_: GateType
    output: int
    inputs: tuple[int]


@dataclass
class Net:
    state = Logic.UNASSIGNED


def read_netlist(file: str | Path):
    file = Path(file)

    with file.open() as f:
        # prefilter blank lines
        lines = [line.rstrip() for line in f if line]

    gates: set[Gate] = set()
    net_list: dict[int, Logic] = {}
    input_nets: list[int] = []
    output_nets: list[int] = []

    for line in lines:
        name, *nets = line.split()
        nets = list(map(int, nets))
        if name in GateType:
            net_list.update((net, Logic.UNASSIGNED) for net in nets)
            *in_, out = nets
            gates.add(Gate(type_=GateType(name), output=out, inputs=tuple(in_)))
        elif name == 'INPUT':
            input_nets.extend(filter(lambda n: n > 0, nets))
        elif name == 'OUTPUT':
            output_nets.extend(filter(lambda n: n > 0, nets))
        else:
            raise RuntimeError(f'unknown gate type {name}')

    return gates, net_list, input_nets, output_nets


def evaluate_gate(gate: Gate, net: dict[int, Logic]) -> Logic:
    match gate.type_, gate.inputs:
        case GateType.INV, [a]:
            return Logic(not net[a])
        case GateType.BUF, [a]:
            return net[a]
        case GateType.AND, [a, b]:
            return Logic(net[a] and net[b])
        case GateType.OR, [a, b]:
            return Logic(net[a] or net[b])
        case GateType.NOR, [a, b]:
            return Logic(not (net[a] or net[b]))
        case GateType.NAND, [a, b]:
            return Logic(not (net[a] and net[b]))
        case _:
            raise TypeError(f'Could not evaluate gate {gate}')


def process_files(netlist_file: str, test_vectors:list[str]):
    for vector in test_vectors:
        gates, net_list, input_nets, output_nets = read_netlist(netlist_file)
            
        test_vector = [True if x == '1' else False for x in vector]

        assert len(test_vector) == len(input_nets)

        for net_id, state in zip(input_nets, test_vector):
            net_list[net_id] = Logic(state)

        stack: set[Gate] = set()
        gates: set[Gate] = set(gates)

        is_assigned = lambda inpt: net_list[inpt] != Logic.UNASSIGNED  # noqa: E731
        is_ready = lambda gate: all(map(is_assigned, gate.inputs))  # noqa: E731

        ready_gates = set(filter(is_ready, gates))
        stack.update(ready_gates)
        gates.difference_update(ready_gates)

        while len(stack) > 0:
            gate = stack.pop()
            output_state = evaluate_gate(gate, net_list)
            net_list[gate.output] = output_state

            ready_gates = set(filter(is_ready, gates))
            stack.update(ready_gates)
            gates.difference_update(ready_gates)

        output = ''
        for net in output_nets:
            match net_list[net]:
                case Logic.HIGH:
                    output += '1'
                case Logic.LOW:
                    output += '0'
                case other:
                    raise RuntimeError(f'Output left unassigned: {net}: {other}')
        
        print(f'{vector} | {output}')


def main():
    files = ['s27', 's298f_2', 's344f_2', 's349f_2']
    for file in files:
        print(f"File: {file}.net:")
        with open(f"tests/{file}.in") as fp:
            tests = [line.rstrip() for line in fp if line]
        process_files(f'circuits/{file}.net', tests)
        print()


if __name__ == '__main__':
    main()
