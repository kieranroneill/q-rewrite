from __future__ import annotations

from abc import ABC, abstractmethod

from q_rewrite.dtos import MetricsDTO, VerificationDTO, VerificationResourceDTO
from q_rewrite.tools import Logger
from q_rewrite.utilities.logging import get_logger
from qiskit.qasm3 import loads as loads_qasm3


class BaseVerifier(ABC):
    def __init__(self, logger: Logger | None = None):
        self._logger: Logger = logger or get_logger()

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

    @abstractmethod
    def equivalence(
        self,
        candidate_circuit: str,
        reference_circuit: str,
    ) -> bool:
        raise NotImplementedError

    @classmethod
    def metrics(cls, circuit: str) -> MetricsDTO:
        """
        Compute  metrics for a Qiskit circuit.

        Counts gates, two-qubit gates, SWAPs, and computes circuit depth directly from the provided QuantumCircuit.

        Args:
            circuit (str): Circuit to measure, in QASM 3.0 format.

        Returns:
            MetricsDTO: Abstract metrics for the supplied circuit.

        Raises:
            ValueError: If the circuit structure is invalid or cannot be measured (for example, if depth computation
            fails).
        """
        """
        Compute abstract metrics for a Qiskit circuit.

        Counts gates, two-qubit gates, SWAPs, and computes circuit depth directly from the provided QuantumCircuit.

        Args:
            circuit (str): Circuit to measure, in QASM 3.0 format.

        Returns:
            MetricsDTO: Abstract metrics for the supplied circuit.

        Raises:
            ValueError: If the circuit structure is invalid or cannot be measured (for example, if depth computation
            fails).
        """
        _circuit = loads_qasm3(circuit)
        two_qubit = 0
        swaps = 0

        for item in _circuit.data:
            arity = len(item.qubits)

            if arity == 2:
                two_qubit += 1

            if item.operation.name == "swap":
                swaps += 1

        return MetricsDTO(
            depth=_circuit.depth(),
            total_gates=_circuit.size(),
            two_qubit_gates=two_qubit,
            swaps=swaps,
        )

    def verify(
        self,
        candidate_circuit: str,
        reference_circuit: str,
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
            candidate_circuit (str): Candidate circuit, in QASM 3.0 format, to verify against the reference circuit.
            reference_circuit (str): Reference circuit, in QASM 3.0 format.
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
        reference_metrics = self.metrics(circuit=reference_circuit)
        reference_resource = VerificationResourceDTO(
            cost=BaseVerifier.cost(
                depth_weight=depth_weight,
                metrics=reference_metrics,
                swap_weight=swap_weight,
                two_qubit_weight=two_qubit_weight,
            ),
            metrics=reference_metrics,
        )
        candidate_metrics = self.metrics(circuit=candidate_circuit)
        candidate_resource = VerificationResourceDTO(
            cost=BaseVerifier.cost(
                depth_weight=depth_weight,
                metrics=candidate_metrics,
                swap_weight=swap_weight,
                two_qubit_weight=two_qubit_weight,
            ),
            metrics=candidate_metrics,
        )

        try:
            equivalent = self.equivalence(reference_circuit=reference_circuit, candidate_circuit=candidate_circuit)
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

