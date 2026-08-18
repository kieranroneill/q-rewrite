from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .base_dto import BaseDTO
from .optimization_history_dto import OptimizationHistoryDTO


@dataclass
class OptimizationDTO(BaseDTO):
    final_circuit: str
    final_cost: float
    history: list[OptimizationHistoryDTO]
    initial_cost: float
    iterations: int
    model_calls: int
    reduction: float
    stopped_due_to_patience: bool
    target_reached: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "final_circuit": self.final_circuit,
            "final_cost": self.final_cost,
            "history": [history.to_dict() for history in self.history],
            "initial_cost": self.initial_cost,
            "iterations": self.iterations,
            "model_calls": self.model_calls,
            "reduction": self.reduction,
            "stopped_due_to_patience": self.stopped_due_to_patience,
            "target_reached": self.target_reached,
        }
