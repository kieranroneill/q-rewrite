from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from q_rewrite.dtos import MetricsDTO, VerificationDTO
from q_rewrite.tools import Logger
from q_rewrite.utilities.logging import get_logger

T = TypeVar("T")


class BaseVerifier(ABC, Generic[T]):
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

    @staticmethod
    @abstractmethod
    def equivalence(
        candidate_circuit: T,
        reference_circuit: T,
    ) -> bool:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def metrics(circuit: T) -> MetricsDTO:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def verify(
        candidate_circuit: T,
        reference_circuit: T,
        depth_weight: float = 1.0,
        swap_weight: float = 10.0,
        two_qubit_weight: float = 5.0
    ) -> VerificationDTO:
        raise NotImplementedError

