from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from q_rewrite.enums import RewriteActionEnum


@dataclass(frozen=True, slots=True)
class CircuitOptimizationProposalDTO:
    action: RewriteActionEnum
    end: int | None
    reason: str
    start: int | None
    parameters: dict[str, Any] = field(default_factory=dict)
