from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Self, TypeVar

from q_rewrite.dtos import SerializedCircuitDTO

Circuit = TypeVar("Circuit")


class BaseParser(ABC, Generic[Circuit]):
    def __init__(self, circuit: SerializedCircuitDTO):
        self._circuit: SerializedCircuitDTO = circuit

    def circuit(self) -> SerializedCircuitDTO:
        return self._circuit

    @classmethod
    @abstractmethod
    def from_circuit(cls, circuit: Circuit) -> Self:
        raise NotImplementedError

    @abstractmethod
    def to_circuit(self) -> Circuit:
        raise NotImplementedError
