from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any

from q_rewrite.clients import ModelClient
from q_rewrite.dtos import OptimizationDTO, CircuitOptimizationProposalDTO
from q_rewrite.enums import RewriteActionEnum
from q_rewrite.tools import Logger
from q_rewrite.utilities.logging import get_logger

Circuit = TypeVar("Circuit")


class BaseOptimizer(ABC, Generic[Circuit]):
    def __init__(self, model_client: ModelClient, logger: Logger | None = None):
        self._model_client: ModelClient = model_client
        self._logger: Logger = logger or get_logger()

    @abstractmethod
    def merge_rotations(
        self,
        circuit: Circuit,
        start: int,
        end: int,
        parameters: dict[str, Any],
    ) -> Circuit:
        raise NotImplementedError

    @abstractmethod
    def optimize(
        self,
        circuit: Circuit,
        max_iterations: int= 100,
        max_model_calls: int = 100,
        patience: int = 5,
        target_reduction: float= 0.10,
    ) -> OptimizationDTO[Circuit]:
        raise NotImplementedError

    @abstractmethod
    def remove_inverse_pair(
        self,
        circuit: Circuit,
        start: int,
        end: int,
        parameters: dict[str, Any],
    ) -> Circuit:
        raise NotImplementedError

    def apply_proposal(self, circuit: Circuit, proposal: CircuitOptimizationProposalDTO) -> Circuit | None:
        if proposal.action == RewriteActionEnum.NOOP:
            return None

        if proposal.start is None or proposal.end is None:
            raise ValueError(
                "non-noop proposal requires start and end"
            )

        if proposal.action == RewriteActionEnum.REMOVE_INVERSE_PAIR:
            return self.remove_inverse_pair(
                circuit=circuit,
                end=proposal.end,
                parameters=proposal.parameters,
                start=proposal.start,
            )

        if proposal.action == RewriteActionEnum.MERGE_ROTATIONS:
            return self.merge_rotations(
                circuit=circuit,
                end=proposal.end,
                parameters=proposal.parameters,
                start=proposal.start,
            )

        raise ValueError(f'unsupported action "{proposal.action}"')
