import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.qasm3 import dumps as dumps_qasm3

from q_rewrite.verifiers import ExpectationVerifier

@pytest.fixture
def verifier():
    return ExpectationVerifier(["Z", "X", "Y"])

class TestEquivalenceSuccess:
    def test_identity_then_removed(self, verifier):
        reference = QuantumCircuit(1)
        reference.h(0)
        reference.x(0)
        reference.x(0)

        candidate = QuantumCircuit(1)
        candidate.h(0)

        result = verifier.verify(reference_circuit=dumps_qasm3(reference), candidate_circuit=dumps_qasm3(candidate))

        assert result.accepted is True
        assert result.equivalent is True
        assert result.reason == "accepted"

class TestNonEquivalentRejection:
    def test_missing_gate(self, verifier):
        reference = QuantumCircuit(2)
        reference.h(0)
        reference.cx(0, 1)

        candidate = QuantumCircuit(2)
        candidate.h(0)

        result = verifier.verify(reference_circuit=dumps_qasm3(reference), candidate_circuit=dumps_qasm3(candidate))

        assert not result.equivalent
        assert not result.accepted
        assert result.reason == "candidate is not equivalent"

    def test_wrong_gate(self, verifier):
        reference = QuantumCircuit(2)
        reference.h(0)
        reference.cx(0, 1)

        candidate = QuantumCircuit(2)
        candidate.h(0)
        candidate.cz(0, 1)

        result = verifier.verify(reference_circuit=dumps_qasm3(reference), candidate_circuit=dumps_qasm3(candidate))

        assert not result.equivalent
        assert not result.accepted
        assert result.reason == "candidate is not equivalent"


class TestInversePairRemoval:
    def test_xx_inverse_pair(self, verifier):
        reference = QuantumCircuit(2)
        reference.h(0)
        reference.cx(0, 1)
        reference.x(0)
        reference.x(0)
        reference.cx(0, 1)

        candidate = QuantumCircuit(2)
        candidate.h(0)
        candidate.cx(0, 1)
        candidate.cx(0, 1)

        result = verifier.verify(reference_circuit=dumps_qasm3(reference), candidate_circuit=dumps_qasm3(candidate))

        assert result.accepted is True
        assert result.equivalent is True
        assert result.reason == "accepted"

    def test_cx_cx_inverse_pair(self, verifier):
        reference = QuantumCircuit(3)
        reference.h(0)
        reference.cx(0, 1)
        reference.cx(0, 2)
        reference.cx(0, 1)
        reference.cx(0, 1)

        candidate = QuantumCircuit(3)
        candidate.h(0)
        candidate.cx(0, 1)
        candidate.cx(0, 2)

        result = verifier.verify(reference_circuit=dumps_qasm3(reference), candidate_circuit=dumps_qasm3(candidate))

        assert result.accepted is True
        assert result.equivalent is True
        assert result.reason == "accepted"


class TestAbstractImprovement:
    def test_depth_improvement_only(self, verifier):
        # two circuits with same unitary but different abstract depth.
        reference = QuantumCircuit(1)
        reference.h(0)
        reference.x(0)
        reference.x(0)
        reference.h(0)
        reference.h(0)

        candidate = QuantumCircuit(1)
        candidate.h(0)

        result = verifier.verify(reference_circuit=dumps_qasm3(reference), candidate_circuit=dumps_qasm3(candidate))

        assert result.accepted is True
        assert result.equivalent is True
        assert result.reason == "accepted"

    def test_two_qubit_reduction(self, verifier):
        reference = QuantumCircuit(3)
        reference.h(0)
        reference.cx(0, 1)
        reference.cx(0, 2)
        reference.cx(0, 1)
        reference.cx(0, 1)

        candidate = QuantumCircuit(3)
        candidate.h(0)
        candidate.cx(0, 1)
        candidate.cx(0, 2)

        result = verifier.verify(reference_circuit=dumps_qasm3(reference), candidate_circuit=dumps_qasm3(candidate))

        assert result.accepted is True
        assert result.equivalent is True
        assert result.reason == "accepted"


class TestResourceConstraints:
    def test_reject_if_two_qubit_increases(self, verifier):
        reference = QuantumCircuit(2)
        reference.h(0)
        reference.cx(0, 1)

        candidate = QuantumCircuit(2)
        candidate.h(0)
        candidate.cx(0, 1)
        candidate.cx(0, 1)
        candidate.cx(0, 1)

        result = verifier.verify(reference_circuit=dumps_qasm3(reference), candidate_circuit=dumps_qasm3(candidate))

        assert result.equivalent is True
        assert result.accepted is False
        assert result.reason == "hardware metrics did not improve"

    def test_reject_if_depth_increases(self, verifier):
        reference = QuantumCircuit(1)
        reference.h(0)

        candidate = QuantumCircuit(1)
        candidate.h(0)
        candidate.x(0)
        candidate.x(0)

        result = verifier.verify(reference_circuit=dumps_qasm3(reference), candidate_circuit=dumps_qasm3(candidate))

        assert result.equivalent is True
        assert result.accepted is False
        assert result.reason == "hardware metrics did not improve"


class TestGlobalPhaseInvariance:
    def test_global_phase_difference(self, verifier):
        # these two circuits differ only by a global phase: X and RZ(pi) X RZ(-pi) are equivalent up to global phase.
        reference = QuantumCircuit(1)
        reference.x(0)

        candidate = QuantumCircuit(1)
        candidate.rz(np.pi, 0)
        candidate.x(0)
        candidate.rz(-np.pi, 0)

        result = verifier.verify(reference_circuit=dumps_qasm3(reference), candidate_circuit=dumps_qasm3(candidate))

        assert result.accepted is False
        assert result.equivalent is True


class TestEdgeCases:
    def test_identical_circuit(self, verifier):
        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)

        result = verifier.verify(reference_circuit=dumps_qasm3(circuit), candidate_circuit=dumps_qasm3(circuit.copy()))

        assert result.equivalent is True
        assert result.accepted is False
        assert result.reason == "no improvement"
        assert result.candidate.cost == result.reference.cost

    def test_empty_circuit(self, verifier):
        reference = QuantumCircuit(1)
        candidate = QuantumCircuit(1)

        result = verifier.verify(reference_circuit=dumps_qasm3(reference), candidate_circuit=dumps_qasm3(candidate))

        assert result.accepted is False
        assert result.equivalent is True
        assert result.reason == "no improvement"
        assert result.candidate.cost == result.reference.cost

    def test_single_qubit_rotations(self, verifier):
        reference = QuantumCircuit(1)
        reference.rx(0.3, 0)
        reference.rx(-0.3, 0)

        candidate = QuantumCircuit(1)

        result = verifier.verify(reference_circuit=dumps_qasm3(reference), candidate_circuit=dumps_qasm3(candidate))

        assert result.accepted is True
        assert result.equivalent is True
        assert result.reason == "accepted"

