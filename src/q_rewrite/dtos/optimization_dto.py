from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from .optimization_history_dto import OptimizationHistoryDTO

Circuit = TypeVar("Circuit")


@dataclass
class OptimizationDTO(Generic[Circuit]):
    final_circuit: Circuit
    final_cost: float
    history: list[OptimizationHistoryDTO]
    initial_cost: float
    iterations: int
    model_calls: int
    reduction: float
    stopped_due_to_patience: bool
    target_reached: bool
