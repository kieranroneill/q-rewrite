from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
from typing import Any


@dataclass
class BaseDTO(ABC):
    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError

    def to_string(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            separators=(",", ":"),
        )
