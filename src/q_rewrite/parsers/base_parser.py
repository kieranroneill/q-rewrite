from q_rewrite.dtos import ModelCircuitDTO


class BaseParser:
    def __init__(self, circuit: ModelCircuitDTO):
        self._circuit: ModelCircuitDTO = circuit

    def circuit(self) -> ModelCircuitDTO:
        return self._circuit
