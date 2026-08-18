from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .base_dto import BaseDTO
from .verification_resource_dto import VerificationResourceDTO


@dataclass
class VerificationDTO(BaseDTO):
    """
    Summarize whether a candidate circuit is equivalent to a reference circuit, whether it improves abstract resource
    metrics, and whether it should be accepted as a valid optimization proposal.

    It is used by the optimizer loop to decide whether to keep or discard a proposed rewrite.

    Attributes:
        accepted (bool): Whether the candidate circuit should be accepted as a valid improvement over the reference
        circuit.
        candidate (VerificationResourceDTO): The metrics and score of the reference circuit.
        equivalent (bool): Whether the candidate circuit is unitary-equivalent to the reference circuit, up to
        global-phase.
        reason (str): Human-readable explanation of the verification outcome, such as "accepted", "no improvement", or
        "candidate is not equivalent".
        reference (VerificationResourceDTO): The metrics and score of the reference circuit.
    """
    accepted: bool
    candidate: VerificationResourceDTO
    equivalent: bool
    reason: str
    reference: VerificationResourceDTO

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "candidate": self.candidate.to_dict(),
            "equivalent": self.equivalent,
            "reason": self.reason,
            "reference": self.reference.to_dict(),
        }
