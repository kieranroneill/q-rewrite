from __future__ import annotations

import json
from typing import Any

from qiskit import QuantumCircuit
from qiskit.circuit.quantumcircuitdata import CircuitInstruction

from .base_optimizer import BaseOptimizer
from q_rewrite.dtos import OptimizationDTO, OptimizationHistoryDTO
from q_rewrite.parsers import QiskitParser
from q_rewrite.verifiers import QiskitVerifier

ROTATION_GATES = {"rx", "ry", "rz"}
REVERSE_INVERSE_GATES = {"x", "y", "z", "h", "cx", "cz", "swap"}

class QiskitOptimizer(BaseOptimizer[QuantumCircuit]):
    @staticmethod
    def _instruction_qubits(circuit: QuantumCircuit, item: CircuitInstruction) -> tuple[int, ...]:
        return tuple(
            circuit.find_bit(qubit).index
            for qubit in item.qubits
        )

    def remove_inverse_pair(
        self,
        circuit: QuantumCircuit,
        start: int,
        end: int,
        parameters: dict[str, Any],
    ) -> QuantumCircuit:
        if start < 0 or end > len(circuit.data):
            raise ValueError("proposal range is out of bounds")

        if end != start + 2:
            raise ValueError(
                "remove_inverse_pair requires an exclusive range of length 2"
            )

        first = circuit.data[start]
        second = circuit.data[start + 1]

        if first.operation.name != second.operation.name:
            raise ValueError("operations are not the same gate")

        if first.operation.name not in REVERSE_INVERSE_GATES:
            raise ValueError("gate is not supported")

        if QiskitOptimizer._instruction_qubits(
            circuit,
            first,
        ) != QiskitOptimizer._instruction_qubits(
            circuit,
            second,
        ):
            raise ValueError("gates act on different qubits")

        result = QuantumCircuit(
            *circuit.qregs,
            *circuit.cregs,
            name=circuit.name,
        )

        for index, item in enumerate(circuit.data):
            if start <= index < end:
                continue

            qargs = QiskitOptimizer._instruction_qubits(
                circuit,
                item,
            )
            cargs = tuple(
                circuit.find_bit(clbit).index
                for clbit in item.clbits
            )

            result.append(
                item.operation,
                qargs,
                cargs,
            )

        return result

    def optimize(
        self,
        circuit: QuantumCircuit,
        max_iterations: int = 100,
        max_model_calls: int = 100,
        patience: int = 5,
        target_reduction: float = 0.10,
    ) -> OptimizationDTO[QuantumCircuit]:
        initial_circuit = circuit.copy()
        initial_metrics = QiskitVerifier.metrics(initial_circuit)
        initial_cost = QiskitVerifier.cost(initial_metrics)
        current_circuit = circuit.copy()
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
                self._logger.debug(f"target cost {target_cost} reached as current cost is {current_cost} after {iteration} iteration(s)")

                break

            if model_calls >= max_model_calls:
                self._logger.debug(f'max model calls {max_model_calls} reached after {iteration} iteration(s)')

                break

            parser = QiskitParser.from_circuit(current_circuit)
            serialized_circuit = parser.circuit()

            self._logger.debug(f"""
Serialized Circuit:
- num_qubuts: {serialized_circuit.num_qubits}
- num_cbits: {serialized_circuit.num_cbits}
- instructions:
{"\n".join(
    json.dumps(
        instruction,
        ensure_ascii=False,
        sort_keys=False,
    )
    for instruction in serialized_circuit.to_dict()["instructions"]
)}
            """)

            self._logger.debug(f'requesting proposal to model "{self._model_client.model()}"')

            proposal = self._model_client.propose(circuit=serialized_circuit)

            self._logger.info(f'''
Model:
- model: {self._model_client.model()}
- calls: {model_calls}
            ''')
            self._logger.info(f'''
Proposal:
- action: "{proposal.action}"
- end: "{proposal.end}"
- parameters: "{json.dumps(proposal.parameters)}"
- reason: "{proposal.reason}"
- start: "{proposal.start}"
            ''')

            model_calls += 1

            try:
                candidate_circuit = self.apply_proposal(circuit=current_circuit, proposal=proposal)

                # if no candidate circuit is created, i.e. "noop" use the current circuit
                if candidate_circuit is None:
                    candidate_circuit = current_circuit.copy()
            except (TypeError, ValueError, IndexError) as e:
                no_improvement += 1

                self._logger.debug(f'failed to apply proposal after {iteration} iteration(s): {e}')

                history.append(OptimizationHistoryDTO[QuantumCircuit](
                    iteration=iteration,
                    accepted=False,
                    circuit=current_circuit,
                    cost=None,
                    equivalent=None,
                    proposal=proposal,
                    metrics=None,
                    reason=f"invalid proposal: {e}",
                ))

                # if no of improvements exceeds the patience, stop
                if no_improvement >= patience:
                    self._logger.debug(f"{no_improvement} of no improvements reached a patience of {patience} after {iteration} iteration(s)")

                    break

                continue

            self._logger.debug(f'applied proposal "{proposal.action}"')

            verification = QiskitVerifier.verify(
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
                no_improvement = 0 # reset the no of improvements on successful acceptance of proposal
            else:
                self._logger.debug(f'verification rejected - "{verification.reason}"')

                no_improvement += 1

                # if no of improvements exceeds the patience, stop
                if no_improvement >= patience:
                    self._logger.debug(f"{no_improvement} of no improvements reached a patience of {patience} after {iteration} iteration(s)")
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

    def merge_rotations(
        self,
        circuit: QuantumCircuit,
        start: int,
        end: int,
        parameters: dict[str, Any],
    ) -> QuantumCircuit:
        if start < 0 or end > len(circuit.data):
            raise ValueError("proposal range is out of bounds")

        if end - start != 2:
            raise ValueError(
                "merge_rotations requires exactly two instructions"
            )

        first = circuit.data[start]
        second = circuit.data[start + 1]

        first_name = first.operation.name
        second_name = second.operation.name

        if first_name not in ROTATION_GATES:
            raise ValueError(
                f"unsupported first rotation {first_name!r}"
            )

        if second_name not in ROTATION_GATES:
            raise ValueError(
                f"unsupported second rotation {second_name!r}"
            )

        if first_name != second_name:
            raise ValueError(
                "rotations must use the same axis"
            )

        first_qubits = tuple(
            circuit.find_bit(qubit).index
            for qubit in first.qubits
        )
        second_qubits = tuple(
            circuit.find_bit(qubit).index
            for qubit in second.qubits
        )

        if len(first_qubits) != 1 or len(second_qubits) != 1:
            raise ValueError(
                "rotations must be single-qubit operations"
            )

        if first_qubits != second_qubits:
            raise ValueError(
                "rotations must use the same qubit"
            )

        claimed_axis = parameters.get("axis")

        if claimed_axis is not None and claimed_axis != first_name:
            raise ValueError(
                f"model axis {claimed_axis!r} does not match "
                f"circuit axis {first_name!r}"
            )

        theta_1 = first.operation.params[0]
        theta_2 = second.operation.params[0]
        merged_theta = theta_1 + theta_2

        result = QuantumCircuit(
            *circuit.qregs,
            *circuit.cregs,
            name=circuit.name,
        )

        for index, instruction in enumerate(circuit.data):
            if index == start:
                qubit = first_qubits[0]

                if first_name == "rx":
                    result.rx(merged_theta, qubit)
                elif first_name == "ry":
                    result.ry(merged_theta, qubit)
                elif first_name == "rz":
                    result.rz(merged_theta, qubit)

            if start <= index < end:
                continue

            qargs = [
                circuit.find_bit(qubit).index
                for qubit in instruction.qubits
            ]
            cargs = [
                circuit.find_bit(clbit).index
                for clbit in instruction.clbits
            ]

            result.append(
                instruction.operation,
                qargs,
                cargs,
            )

        return result
