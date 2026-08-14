from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from .serialized_circuit_instruction_dto import SerializedCircuitInstructionDTO


@dataclass(frozen=True)
class SerializedCircuitDTO:
    instructions: list[SerializedCircuitInstructionDTO]
    num_qubits: int
    num_cbits: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
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
