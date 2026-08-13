from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from .circuit_summary_instruction_dto import CircuitSummaryInstructionDTO


@dataclass
class CircuitSummaryDTO:
    instructions: list[CircuitSummaryInstructionDTO]
    num_qubits: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "instructions": [instruction.to_dict() for instruction in self.instructions],
            "num_qubits": self.num_qubits,
        }

    def to_string(self) -> str:
        return json.dumps(self.to_dict())

