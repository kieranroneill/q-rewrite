from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any


@dataclass
class MetricsDTO:
    """
    Summarize circuit complexity by isolating the most significant metrics.

    Attributes:
        depth (int): Circuit depth, defined as the length of the longest dependency chain of operations.
        swaps (int): Number of SWAP gates in the circuit.
        total_gates (int): Total number of instructions (gates and other operations) in the circuit.
        two_qubit_gates (int): Number of two-qubit gates in the circuit.
    """
    depth: int
    swaps: int
    total_gates: int
    two_qubit_gates: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "depth": self.depth,
            "swaps": self.swaps,
            "total_gates": self.total_gates,
            "two_qubit_gates": self.two_qubit_gates,
        }

    def to_string(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            separators=(",", ":"),
        )
