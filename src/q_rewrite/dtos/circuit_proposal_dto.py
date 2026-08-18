from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .base_dto import BaseDTO


@dataclass
class CircuitProposalDTO(BaseDTO):
    qasm: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "qasm": self.qasm,
            "reason": self.reason,
        }
