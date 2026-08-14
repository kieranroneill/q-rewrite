from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from .circuit_optimization_proposal_dto import CircuitOptimizationProposalDTO
from .metrics_dto import MetricsDTO

Circuit = TypeVar("Circuit")


@dataclass
class OptimizationHistoryDTO(Generic[Circuit]):
    accepted: bool
    circuit: Circuit
    cost: float | None
    equivalent: bool | None
    iteration: int
    proposal: CircuitOptimizationProposalDTO
    metrics: MetricsDTO | None
    reason: str
