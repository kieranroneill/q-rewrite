from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from .circuit_summary_instruction_dto import CircuitSummaryInstructionDTO


@dataclass(frozen=True)
class CircuitSummaryDTO:
    instructions: list[CircuitSummaryInstructionDTO]
    num_qubits: int
    has_measurements: bool = False
    num_cbits: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "has_measurements": self.has_measurements,
            "instructions": [instruction.to_dict() for instruction in self.instructions],
            "num_cbits": self.num_cbits,
            "num_qubits": self.num_qubits,
        }

    def to_string(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            separators=(",", ":"),
        )

