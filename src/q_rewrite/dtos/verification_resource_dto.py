from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .base_dto import BaseDTO
from .metrics_dto import MetricsDTO


@dataclass
class VerificationResourceDTO(BaseDTO):
    """
    Metrics outling the complexity of a circuit and the weighted cost.

    Attributes:
        cost (float): The hardware-aware cost of the circuit.
        metrics (MetricsDTO): The most significant metrics detail the complexity of the circuit.
    """
    cost: float
    metrics: MetricsDTO

    def to_dict(self) -> dict[str, Any]:
        return {
            "cost": self.cost,
            "metrics": self.metrics.to_dict(),
        }
