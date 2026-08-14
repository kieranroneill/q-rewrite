from __future__ import annotations

import ast
import math
import operator
from typing import Any

from qiskit import QuantumCircuit

from .base_parser import BaseParser
from q_rewrite.dtos import SerializedCircuitDTO, SerializedCircuitInstructionDTO


class QiskitParser(BaseParser[QuantumCircuit]):
    ##
    # private static methods
    ##

    @staticmethod
    def _append_instruction(
        circuit: QuantumCircuit,
        instruction: SerializedCircuitInstructionDTO,
    ) -> None:
        """
        Append one model instruction to a Qiskit quantum circuit.

        Gate names are normalized to lowercase. Numeric parameter expressions
        are converted through `_parse_parameter`, and qubit indexes are
        validated before the corresponding Qiskit gate method is called.

        Args:
            circuit (QuantumCircuit): Circuit receiving the instruction.
            instruction (SerializedCircuitInstructionDTO): Model instruction to add.

        Returns:
            None: The circuit is modified in place.

        Raises:
            ValueError: If the instruction contains an invalid qubit index,
                unsupported gate, unsupported parameter expression, or an
                incorrect number of parameters.
        """
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
                f"{gate} requires {expected} parameters, received {len(parameters)}"
            )

        method(*parameters, *qubits)

    @staticmethod
    def _parse_parameter(value: str) -> float:
        """
        Parse a restricted numeric quantum-gate parameter expression.

        Supported expressions include numeric literals, the constants `pi`,
        `tau`, and `e`, unary plus and minus, and the binary operators
        addition, subtraction, multiplication, division, and exponentiation.

        Examples of supported expressions include:

            0.5
            -0.25
            pi / 2
            2 * pi
            (pi / 4) + 0.1

        The expression is evaluated using an explicit AST allowlist rather
        than Python's eval function.

        Args:
            value (str): Numeric parameter expression.

        Returns:
            float: Evaluated numeric parameter value.

        Raises:
            ValueError: If the expression is empty, contains an unsupported
                name or operator, or is not a supported numeric expression.
            SyntaxError: If the value cannot be parsed as a Python expression.
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
        circuit: QuantumCircuit,
        instruction: SerializedCircuitInstructionDTO,
    ) -> None:
        """
        Validate that all instruction qubit indexes exist in the circuit.

        Args:
            circuit (QuantumCircuit): Circuit whose qubit range is used.
            instruction (SerializedCircuitInstructionDTO): Instruction to validate.

        Returns:
            None: The method returns normally when all indexes are valid.

        Raises:
            ValueError: If a qubit index is negative or greater than or equal
                to the circuit's number of qubits.
        """
        for qubit in instruction.qubits:
            if qubit < 0 or qubit >= circuit.num_qubits:
                raise ValueError(f'invalid qubit index "{qubit}" for gate {instruction.gate!r}')

    ##
    # public static methods
    ##

    @classmethod
    def from_circuit(cls, circuit: QuantumCircuit) -> "QiskitParser":
        """
        Create a parser from a Qiskit quantum circuit.

        Each Qiskit instruction is converted into a
        ModelCircuitInstructionDTO. Instruction indexes follow the order of
        `circuit.data`, and qubit indexes are converted from Qiskit's qubit
        objects into integer positions.

        Gate parameters are converted to strings. This preserves their textual
        representation for model prompting, but symbolic parameter identity
        is not preserved.

        Args:
            circuit (QuantumCircuit): Source Qiskit circuit.

        Returns:
            QiskitParser: Parser containing the model representation of the
                supplied circuit.

        Raises:
            ValueError: If the circuit contains unsupported data that cannot be
                converted into the model representation.
        """
        instructions: list[SerializedCircuitInstructionDTO] = []

        for index, item in enumerate(circuit.data):
            instructions.append(SerializedCircuitInstructionDTO(
                gate=item.operation.name.lower(),
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
            circuit=SerializedCircuitDTO(
                instructions=instructions,
                num_qubits=circuit.num_qubits,
            ),
        )

    ##
    # public methods
    ##

    def to_circuit(self) -> QuantumCircuit:
        """
         Reconstruct a Qiskit circuit from the model circuit DTO.

         A new QuantumCircuit is created with the number of qubits stored in
         the model representation. Instructions are appended in DTO order and
         are validated before being added.

         The original model circuit and its instructions are not modified.

         Returns:
             QuantumCircuit: Reconstructed Qiskit circuit.

         Raises:
             ValueError: If an instruction contains an invalid qubit index,
                 unsupported gate, unsupported parameter expression, or an
                 invalid parameter count.
         """
        circuit = QuantumCircuit(
            self._circuit.num_qubits,
        )

        for instruction in self._circuit.instructions:
            self._append_instruction(
                circuit,
                instruction,
            )

        return circuit

