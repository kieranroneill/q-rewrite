from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProposalCircuitDTO:
    action: str
    end: int | None
    reason: str
    start: int | None
