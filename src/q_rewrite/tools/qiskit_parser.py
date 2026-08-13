from qiskit import QuantumCircuit

from q_rewrite.dtos import CircuitSummaryDTO, CircuitSummaryInstructionDTO


class QiskitParser:
    def summarize(self, circuit: QuantumCircuit) -> CircuitSummaryDTO:
        instructions: list[CircuitSummaryInstructionDTO] = []

        for index, item in enumerate(circuit.data):
            instructions.append(CircuitSummaryInstructionDTO(
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

        return CircuitSummaryDTO(
            instructions=instructions,
            num_qubits=circuit.num_qubits,
        )
