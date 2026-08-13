from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

from q_rewrite.dtos import MetricsDTO, VerificationDTO, VerificationResourceDTO


class Verifier:
    def __init__(self, ):
        pass

    @staticmethod
    def cost(metrics: MetricsDTO, depth_weight: float = 1.0, swap_weight: float = 10.0, two_qubit_weight: float = 5.0) -> float:
        """
        Compute an abstract hardware-agnostic cost from circuit metrics.

        This is a simple weighted sum of depth, two-qubit gates, and SWAPs. The weights reflect a rough priority: SWAPs
        are most expensive, followed by two-qubit gates, then depth.

        Args:
            metrics (MetricsDTO): Abstract circuit metrics.
            depth_weight (float): Weight for depth in the score calculation. Defaults to 1.0.
            swap_weight (float): Weight for SWAPs in the score calculation. Defaults to 10.0.
            two_qubit_weight (float): Weight for two-qubit gates in the score calculation. Defaults to 5.0.

        Returns:
            float: Scalar cost where lower values indicate a cheaper circuit.
        """
        return (
            (depth_weight * metrics.depth) +
            (two_qubit_weight * metrics.two_qubit_gates) +
            (swap_weight * metrics.swaps)
        )

    @staticmethod
    def equivalence(
        candidate_circuit: QuantumCircuit,
        reference_circuit: QuantumCircuit,
    ) -> bool:
        """
        Check whether two circuits are unitary-equivalent up to global-phase.

        This method computes the full unitary matrix for each circuit and compares them, allowing for a global phase
        difference. Measurements are removed before comparison, as they are not part of the unitary.

        **NOTE**: The check is exact up to numerical tolerance and is feasible only for relatively small circuits due to
        the exponential cost of constructing the full unitary.

        Args:
            candidate_circuit (qiskit.QuantumCircuit): Candidate circuit.
            reference_circuit (qiskit.QuantumCircuit): Reference circuit to compare.

        Returns:
            bool: True if the circuits are equivalent up to global-phase, False otherwise.

        Raises:
            Exception: If unitary construction or comparison fails (for example, due to unsupported operations or
            excessive circuit size).
        """
        if reference_circuit.num_qubits != candidate_circuit.num_qubits:
            return False

        lhs = reference_circuit.remove_final_measurements(inplace=False)
        rhs = candidate_circuit.remove_final_measurements(inplace=False)

        if lhs is None or rhs is None:
            raise Exception("failed to remove measurements")

        reference_operator = Operator(lhs).data
        candidate_operator = Operator(rhs).data

        overlap = np.vdot(
            reference_operator.flatten(),
            candidate_operator.flatten(),
        )

        if abs(overlap) < 1e-12:
            return False

        phase = overlap / abs(overlap)

        return np.allclose(
            reference_operator,
            phase * candidate_operator,
            atol=1e-8,
            rtol=1e-8,
        )

    @staticmethod
    def metrics(circuit: QuantumCircuit) -> MetricsDTO:
        """
        Compute abstract metrics for a Qiskit circuit.

        Counts gates, two-qubit gates, SWAPs, and computes circuit depth directly from the provided QuantumCircuit.

        Args:
            circuit (qiskit.QuantumCircuit): Circuit to measure.

        Returns:
            MetricsDTO: Abstract metrics for the supplied circuit.

        Raises:
            ValueError: If the circuit structure is invalid or cannot be measured (for example, if depth computation
            fails).
        """
        two_qubit = 0
        swaps = 0

        for item in circuit.data:
            arity = len(item.qubits)

            if arity == 2:
                two_qubit += 1

            if item.operation.name == "swap":
                swaps += 1

        return MetricsDTO(
            depth=circuit.depth(),
            total_gates=circuit.size(),
            two_qubit_gates=two_qubit,
            swaps=swaps,
        )

    @staticmethod
    def verify(
        candidate_circuit: QuantumCircuit,
        reference_circuit: QuantumCircuit,
        depth_weight: float = 1.0,
        swap_weight: float = 10.0,
        two_qubit_weight: float = 5.0
    ) -> VerificationDTO:
        """
        Verify a candidate circuit against a reference circuit.

        This method checks unitary equivalence, compares abstract resource metrics (depth and two-qubit gate count),
        and determines whether the candidate should be accepted as a valid optimization proposal. A candidate is
        accepted only if it is equivalent to the reference and the cost is lower than the reference cost.

        Args:
            candidate_circuit (qiskit.QuantumCircuit): Candidate circuit to verify against the reference circuit.
            reference_circuit (qiskit.QuantumCircuit): Reference circuit.
            depth_weight (float): Weight for depth in the score calculation. Defaults to 1.0.
            swap_weight (float): Weight for SWAPs in the score calculation. Defaults to 10.0.
            two_qubit_weight (float): Weight for two-qubit gates in the score calculation. Defaults to 5.0.

        Returns:
            VerificationDTO: Verification result summarizing equivalence, resource validity, acceptance, and a
            human-readable reason.

        Raises:
            ValueError: If the circuit structure is invalid or cannot be measured (for example, if depth computation
            fails).
        """
        reference_metrics = Verifier.metrics(circuit=reference_circuit)
        reference_resource = VerificationResourceDTO(
            cost=Verifier.cost(
                depth_weight=depth_weight,
                metrics=reference_metrics,
                swap_weight=swap_weight,
                two_qubit_weight=two_qubit_weight,
            ),
            metrics=reference_metrics,
        )
        candidate_metrics = Verifier.metrics(circuit=candidate_circuit)
        candidate_resource = VerificationResourceDTO(
            cost=Verifier.cost(
                depth_weight=depth_weight,
                metrics=candidate_metrics,
                swap_weight=swap_weight,
                two_qubit_weight=two_qubit_weight,
            ),
            metrics=candidate_metrics,
        )

        try:
            equivalent = Verifier.equivalence(reference_circuit, candidate_circuit)
        except Exception as e:
            return VerificationDTO(
                accepted=False,
                candidate=candidate_resource,
                equivalent=False,
                reason=f"equivalence check failed: {e}",
                reference=reference_resource,
            )

        # candidate is at least as good as the reference
        valid = (
            candidate_metrics.two_qubit_gates <= reference_metrics.two_qubit_gates
            and candidate_metrics.depth <= reference_metrics.depth
        )
        # lower cost is an improvement
        improvement = candidate_resource.cost < reference_resource.cost
        # if the circuits are equivalent and the cost is lower, the circuit is accepted
        accepted = equivalent and improvement

        if not equivalent:
            reason = "candidate is not equivalent"
        elif not valid:
            reason = "hardware metrics did not improve"
        elif not accepted:
            reason = "no improvement"
        else:
            reason = "accepted"

        return VerificationDTO(
            accepted=accepted,
            candidate=candidate_resource,
            equivalent=equivalent,
            reason=reason,
            reference=reference_resource,
        )
