from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Self, TypeVar

from q_rewrite.dtos import ModelCircuitDTO

Circuit = TypeVar("Circuit")


class BaseParser(ABC, Generic[Circuit]):
    def __init__(self, circuit: ModelCircuitDTO):
        self._circuit: ModelCircuitDTO = circuit

    def circuit(self) -> ModelCircuitDTO:
        return self._circuit

    @classmethod
    @abstractmethod
    def from_circuit(cls, circuit: Circuit) -> Self:
        raise NotImplementedError

    @abstractmethod
    def to_circuit(self) -> Circuit:
        raise NotImplementedError
