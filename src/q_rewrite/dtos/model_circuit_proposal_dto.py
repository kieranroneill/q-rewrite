from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ModelCircuitProposalDTO:
    action: str
    end: int | None
    reason: str
    start: int | None
