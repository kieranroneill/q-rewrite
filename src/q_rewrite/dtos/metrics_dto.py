from __future__ import annotations

from dataclasses import dataclass


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
