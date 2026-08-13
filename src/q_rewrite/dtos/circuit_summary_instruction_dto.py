from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any


@dataclass(frozen=True)
class CircuitSummaryInstructionDTO:
    gate: str
    index: int
    parameters: list[str]
    qubits: list[int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate": self.gate,
            "index": self.index,
            "parameters": self.parameters,
            "qubits": self.qubits
        }

    def to_string(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            separators=(",", ":"),
        )
