from __future__ import annotations

from q_rewrite.clients import ModelClient
from q_rewrite.dtos import OptimizationDTO, OptimizationHistoryDTO
from q_rewrite.tools import Logger
from q_rewrite.utilities.logging import get_logger
from q_rewrite.verifiers import BaseVerifier


class Optimizer:
    def __init__(self, model_client: ModelClient, verifier: BaseVerifier, logger: Logger | None = None):
        self._model_client: ModelClient = model_client
        self._logger: Logger = logger or get_logger()
        self._verifier = verifier

    def optimize(
        self,
        circuit: str,
        max_iterations: int= 100,
        max_model_calls: int = 100,
        patience: int = 5,
        target_reduction: float= 0.10,
    ) -> OptimizationDTO:
        initial_circuit = str(circuit)
        initial_metrics = self._verifier.metrics(initial_circuit)
        initial_cost = self._verifier.cost(initial_metrics)
        current_circuit = str(circuit)
        current_cost = initial_cost
        no_improvement = 0
        model_calls = 0
        history: list[OptimizationHistoryDTO] = []
        target_cost = initial_cost * (1.0 - target_reduction)

        self._logger.info(f'''
-------------------------- INITIALIZATION --------------------------
Metrics:
    - depth: {initial_metrics.depth}
    - swaps: {initial_metrics.swaps}
    - total_gates: {initial_metrics.total_gates}
    - two_qubit_gates: {initial_metrics.two_qubit_gates}

Costs:
    - cost of initial circuit: {initial_cost}
    - target cost: {target_cost}
                ''')

        if not 0.0 <= target_reduction < 1.0:
            raise ValueError("target_reduction must be in [0, 1)")

        if max_iterations < 1:
            raise ValueError("max_iterations must be positive")

        if max_model_calls < 1:
            raise ValueError("max_model_calls must be positive")

        if patience < 1:
            raise ValueError("patience must be positive")

        for iteration in range(max_iterations):
            self._logger.info(f"""
        -------------------------- ITERATION {iteration} of {max_iterations} --------------------------
                    """)
            if current_cost <= target_cost:
                self._logger.debug(
                    f"target cost {target_cost} reached as current cost is {current_cost} after {iteration} iteration(s)")

                break

            if model_calls >= max_model_calls:
                self._logger.debug(f'max model calls {max_model_calls} reached after {iteration} iteration(s)')

                break

            self._logger.debug(f'requesting optimizations from model "{self._model_client.model()}"')

            proposal = self._model_client.propose(qasm=current_circuit)

            self._logger.info(f'''
Model:
    - model: {self._model_client.model()}
    - calls: {model_calls}
            ''')
            self._logger.info(f'''
Proposal:
    - qasm:
    """
    {proposal.qasm}
    """
    - reason: {proposal.reason}
            ''')

            model_calls += 1
            candidate_circuit = str(proposal.qasm)
            verification = self._verifier.verify(
                reference_circuit=current_circuit,
                candidate_circuit=candidate_circuit,
            )

            self._logger.info(f'''
Current Metrics:
    - depth: {verification.candidate.metrics.depth}
    - swaps: {verification.candidate.metrics.swaps}
    - total_gates: {verification.candidate.metrics.total_gates}
    - two_qubit_gates: {verification.candidate.metrics.two_qubit_gates}

Current Costs:
    - current cost: {verification.candidate.cost}

Verification:
    - accepted: {verification.accepted}
    - equivalent: {verification.equivalent}
    - reason: {verification.reason}
            ''')

            history.append(OptimizationHistoryDTO(
                iteration=iteration,
                accepted=verification.accepted,
                circuit=candidate_circuit,
                cost=verification.candidate.cost,
                equivalent=verification.equivalent,
                proposal=proposal,
                metrics=verification.candidate.metrics,
                reason=verification.reason,
            ))

            if verification.accepted:
                self._logger.debug(f'verification accepted - "{verification.reason}"')

                current_circuit = candidate_circuit
                current_cost = verification.candidate.cost
                no_improvement = 0  # reset the no of improvements on successful acceptance of proposal
            else:
                self._logger.debug(f'verification rejected - "{verification.reason}"')

                no_improvement += 1

                # if no of improvements exceeds the patience, stop
                if no_improvement >= patience:
                    self._logger.debug(
                        f"{no_improvement} of no improvements reached a patience of {patience} after {iteration} iteration(s)")
                    break

        self._logger.info("""
-------------------------- END ITERATIONS --------------------------
        """)

        reduction = (
            0.0
            if initial_cost == 0
            else 1.0 - current_cost / initial_cost
        )

        return OptimizationDTO(
            final_circuit=current_circuit,
            final_cost=current_cost,
            history=history,
            initial_cost=initial_cost,
            iterations=len(history),
            model_calls=model_calls,
            reduction=reduction,
            stopped_due_to_patience=no_improvement >= patience,
            target_reached=current_cost <= target_cost,
        )
