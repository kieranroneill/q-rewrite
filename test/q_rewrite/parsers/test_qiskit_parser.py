import numpy as np
from qiskit.circuit import QuantumCircuit
from qiskit.quantum_info import Operator

from q_rewrite.parsers import QiskitParser

def _test_circuit_parsing(circuit: QuantumCircuit) -> tuple[QiskitParser, QuantumCircuit]:
    parser = QiskitParser.from_qiskit_circuit(circuit)
    reconstructed_circuit = parser.to_qiskit_circuit()

    assert len(parser.circuit().instructions) == circuit.size()
    assert circuit.num_qubits == reconstructed_circuit.num_qubits
    assert circuit.num_clbits == reconstructed_circuit.num_clbits

    original_operator = Operator(circuit).data
    reconstructed_operator = Operator(reconstructed_circuit).data

    overlap = np.vdot(
        original_operator.flatten(),
        reconstructed_operator.flatten(),
    )

    assert abs(overlap) > 1e-12

    phase = overlap / abs(overlap)

    assert np.allclose(
        original_operator,
        phase * reconstructed_operator,
        atol=1e-8,
        rtol=1e-8,
    )

    return parser, reconstructed_circuit

def test_empty_circuit() -> None:
    circuit = QuantumCircuit(1)

    parser, reconstructed_circuit = _test_circuit_parsing(circuit)

    assert parser.circuit().instructions == []


def test_single_qubit_gates() -> None:
    circuit = QuantumCircuit(1)

    circuit.x(0)
    circuit.y(0)
    circuit.z(0)
    circuit.h(0)
    circuit.s(0)
    circuit.sdg(0)
    circuit.t(0)
    circuit.tdg(0)

    parser, reconstructed_circuit = _test_circuit_parsing(circuit)

    assert [
       instruction.gate
       for instruction in parser.circuit().instructions
    ] == ["x", "y", "z", "h", "s", "sdg", "t", "tdg"]

def test_bell_circuit() -> None:
    circuit = QuantumCircuit(2)

    circuit.h(0)
    circuit.cx(0, 1)

    parser, reconstructed_circuit = _test_circuit_parsing(circuit)

    assert [
       instruction.gate
       for instruction in parser.circuit().instructions
    ] == ["h", "cx"]
    assert [
       instruction.qubits
       for instruction in parser.circuit().instructions
    ] == [[0], [0, 1]]

def test_inverse_pair() -> None:
    circuit = QuantumCircuit(2)

    circuit.h(0)
    circuit.cx(0, 1)
    circuit.x(0)
    circuit.x(0)
    circuit.cx(0, 1)

    parser, reconstructed_circuit = _test_circuit_parsing(circuit)

    assert [
       instruction.gate
       for instruction in parser.circuit().instructions
    ] == ["h", "cx", "x", "x", "cx"]
    assert [
       instruction.qubits
       for instruction in parser.circuit().instructions
    ] == [[0], [0, 1], [0], [0], [0, 1]]

def test_ghz4() -> None:
    circuit = QuantumCircuit(4)

    circuit.h(0)
    circuit.cx(0, 1)
    circuit.cx(1, 2)
    circuit.cx(2, 3)

    parser, reconstructed_circuit = _test_circuit_parsing(circuit)

    assert [
       instruction.gate
       for instruction in parser.circuit().instructions
    ] == ["h", "cx", "cx", "cx"]
    assert [
       instruction.qubits
       for instruction in parser.circuit().instructions
    ] == [[0], [0, 1], [1, 2], [2, 3]]

def test_qft3_style() -> None:
    circuit = QuantumCircuit(3)

    circuit.h(0)
    circuit.cp(np.pi / 2, 1, 0)
    circuit.cp(np.pi / 4, 2, 0)

    circuit.h(1)
    circuit.cp(np.pi / 2, 2, 1)

    circuit.h(2)
    circuit.swap(0, 2)

    parser, reconstructed_circuit = _test_circuit_parsing(circuit)

    assert [
       instruction.gate
       for instruction in parser.circuit().instructions
    ] == ["h", "cp", "cp", "h", "cp", "h", "swap"]

def test_reversible_subcircuit() -> None:
    circuit = QuantumCircuit(3)

    circuit.x(0)
    circuit.h(1)
    circuit.cx(0, 1)
    circuit.ccx(0, 1, 2)
    circuit.swap(1, 2)
    circuit.cz(0, 2)

    parser, reconstructed_circuit = _test_circuit_parsing(circuit)

    assert [
       instruction.gate
       for instruction in parser.circuit().instructions
    ] == ["x", "h", "cx", "ccx", "swap", "cz"]

def test_qaoa_triangle() -> None:
    circuit = QuantumCircuit(3)

    for qubit in range(3):
        circuit.h(qubit)

    gamma = 0.7
    beta = 1.1

    # edge (0, 1).
    circuit.cx(0, 1)
    circuit.rz(gamma, 1)
    circuit.cx(0, 1)

    # edge (1, 2).
    circuit.cx(1, 2)
    circuit.rz(gamma, 2)
    circuit.cx(1, 2)

    # edge (0, 2).
    circuit.cx(0, 2)
    circuit.rz(gamma, 2)
    circuit.cx(0, 2)

    for qubit in range(3):
        circuit.rx(beta, qubit)

    parser, reconstructed_circuit = _test_circuit_parsing(circuit)

    assert [
       instruction.gate
       for instruction in parser.circuit().instructions
    ] == ["h", "h", "h",
          "cx", "rz", "cx",
          "cx", "rz", "cx",
          "cx", "rz", "cx",
          "rx", "rx", "rx"
    ]

