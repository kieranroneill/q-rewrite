from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .base_dto import BaseDTO
from .circuit_proposal_dto import CircuitProposalDTO
from .metrics_dto import MetricsDTO


@dataclass
class OptimizationHistoryDTO(BaseDTO):
    accepted: bool
    circuit: str
    cost: float | None
    equivalent: bool | None
    iteration: int
    proposal: CircuitProposalDTO
    metrics: MetricsDTO | None
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "circuit": self.circuit,
            "cost": self.cost,
            "equivalent": self.equivalent,
            "iteration": self.iteration,
            "proposal": self.proposal.to_dict(),
            "metrics": self.metrics.to_dict() if self.metrics else None,
            "reason": self.reason,
        }
