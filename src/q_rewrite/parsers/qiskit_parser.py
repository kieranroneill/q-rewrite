from __future__ import annotations

import ast
import math
import operator
from typing import Any

import qiskit

from .base_parser import BaseParser
from q_rewrite.dtos import ModelCircuitDTO, ModelCircuitInstructionDTO


class QiskitParser(BaseParser):
    ##
    # private static methods
    ##

    @staticmethod
    def _append_instruction(
        circuit: qiskit.QuantumCircuit,
        instruction: ModelCircuitInstructionDTO,
    ) -> None:
        gate = instruction.gate.lower()
        qubits = instruction.qubits
        parameters = [
            QiskitParser._parse_parameter(parameter)
            for parameter in instruction.parameters
        ]

        QiskitParser._validate_qubits(
            circuit,
            instruction,
        )

        # Gates with no parameters.
        no_parameter_gates = {
            "id": circuit.id,
            "i": circuit.id,
            "x": circuit.x,
            "y": circuit.y,
            "z": circuit.z,
            "h": circuit.h,
            "s": circuit.s,
            "sdg": circuit.sdg,
            "t": circuit.t,
            "tdg": circuit.tdg,
            "sx": circuit.sx,
            "sxdg": circuit.sxdg,
            "cx": circuit.cx,
            "cnot": circuit.cx,
            "cy": circuit.cy,
            "cz": circuit.cz,
            "swap": circuit.swap,
            "ch": circuit.ch,
            "ccx": circuit.ccx,
            "toffoli": circuit.ccx,
        }

        if gate in no_parameter_gates:
            method = no_parameter_gates[gate]
            method(*qubits)
            return

        # Gates with parameters.
        parameterized_gates = {
            "p": circuit.p,
            "phase": circuit.p,
            "rx": circuit.rx,
            "ry": circuit.ry,
            "rz": circuit.rz,
            "r": circuit.r,
            "u": circuit.u,
            "u1": circuit.p,
            "u2": circuit.u,
            "u3": circuit.u,
            "cp": circuit.cp,
            "crx": circuit.crx,
            "cry": circuit.cry,
            "crz": circuit.crz,
        }

        if gate not in parameterized_gates:
            raise ValueError(
                f"Unsupported gate in model circuit: {instruction.gate!r}"
            )

        method = parameterized_gates[gate]

        if gate in {"u1"}:
            if len(parameters) != 1:
                raise ValueError("u1 requires one parameter")

            method(parameters[0], *qubits)
            return

        if gate in {"u2"}:
            if len(parameters) != 2:
                raise ValueError("u2 requires two parameters")

            method(parameters[0], parameters[1], *qubits)
            return

        if gate in {"u3", "u"}:
            if len(parameters) != 3:
                raise ValueError("u/u3 requires three parameters")

            method(
                parameters[0],
                parameters[1],
                parameters[2],
                *qubits,
            )
            return

        expected_parameter_counts = {
            "p": 1,
            "phase": 1,
            "rx": 1,
            "ry": 1,
            "rz": 1,
            "r": 2,
            "cp": 1,
            "crx": 1,
            "cry": 1,
            "crz": 1,
        }

        expected = expected_parameter_counts[gate]

        if len(parameters) != expected:
            raise ValueError(
                f"{gate} requires {expected} parameters, "
                f"received {len(parameters)}"
            )

        method(*parameters, *qubits)

    @staticmethod
    def _parse_parameter(value: str) -> float:
        """
        Parse safe numeric expressions such as:
            0.5
            -0.25
            pi / 2
            2 * pi
        """
        expression = value.strip()

        if not expression:
            raise ValueError("empty gate parameter")

        tree = ast.parse(expression, mode="eval")

        allowed_names = {
            "pi": math.pi,
            "tau": math.tau,
            "e": math.e,
        }

        binary_operators: dict[type[ast.operator], Any] = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
        }

        unary_operators: dict[type[ast.unaryop], Any] = {
            ast.UAdd: operator.pos,
            ast.USub: operator.neg,
        }

        def evaluate(node: ast.AST) -> float:
            if isinstance(node, ast.Constant):
                if isinstance(node.value, int | float):
                    return float(node.value)

                raise ValueError(
                    f"Unsupported constant: {node.value!r}"
                )

            if isinstance(node, ast.Name):
                if node.id in allowed_names:
                    return allowed_names[node.id]

                raise ValueError(
                    f"Unsupported symbolic parameter: {node.id!r}"
                )

            if isinstance(node, ast.BinOp):
                operation = binary_operators.get(type(node.op))

                if operation is None:
                    raise ValueError(
                        f"Unsupported operator: {type(node.op).__name__}"
                    )

                return float(
                    operation(
                        evaluate(node.left),
                        evaluate(node.right),
                    )
                )

            if isinstance(node, ast.UnaryOp):
                operation = unary_operators.get(type(node.op))

                if operation is None:
                    raise ValueError(
                        f"Unsupported unary operator: "
                        f"{type(node.op).__name__}"
                    )

                return float(operation(evaluate(node.operand)))

            raise ValueError(
                f"Unsupported parameter expression: {expression!r}"
            )

        return evaluate(tree.body)

    @staticmethod
    def _validate_qubits(
        circuit: qiskit.QuantumCircuit,
        instruction: ModelCircuitInstructionDTO,
    ) -> None:
        for qubit in instruction.qubits:
            if qubit < 0 or qubit >= circuit.num_qubits:
                raise ValueError(f'invalid qubit index "{qubit}" for gate {instruction.gate!r}')

    ##
    # public static methods
    ##

    @staticmethod
    def from_qiskit_circuit(circuit: qiskit.QuantumCircuit) -> "QiskitParser":
        instructions: list[ModelCircuitInstructionDTO] = []

        for index, item in enumerate(circuit.data):
            instructions.append(ModelCircuitInstructionDTO(
                gate=item.operation.name,
                index=index,
                parameters=[
                    str(parameter)
                    for parameter in item.operation.params
                ],
                qubits=[
                    circuit.find_bit(qubit).index
                    for qubit in item.qubits
                ]
            ))

        return QiskitParser(
            circuit=ModelCircuitDTO(
                instructions=instructions,
                num_qubits=circuit.num_qubits,
            ),
        )

    ##
    # public methods
    ##

    def to_qiskit_circuit(self) -> qiskit.QuantumCircuit:
        circuit = qiskit.QuantumCircuit(
            self._circuit.num_qubits,
        )

        for instruction in self._circuit.instructions:
            self._append_instruction(
                circuit,
                instruction,
            )

        return circuit

