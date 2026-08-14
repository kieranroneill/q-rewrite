import json
import logging

from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
from openai.types.shared_params import ResponseFormatJSONObject

from q_rewrite.dtos import SerializedCircuitDTO, CircuitOptimizationProposalDTO
from q_rewrite.enums import RewriteActionEnum
from q_rewrite.utilities.logging import get_logger

class ModelClient:
    def __init__(
        self,
        model: str,
        base_url: str,
        api_key: str | None = None,
        logger: logging.Logger | None = None,
    ):
        self._client = OpenAI(
            base_url=f"{base_url}/v1",
            api_key=api_key,
        )
        self._logger = logger or get_logger()
        self._model = model

    def model(self):
        return self._model

    def propose(self, circuit: SerializedCircuitDTO) -> CircuitOptimizationProposalDTO:
        system = """
You are a quantum-circuit optimization assistant.

Inspect the supplied circuit summary and propose at most one local
rewrite. The rewrite must preserve the circuit's behavior.

Return exactly one JSON object and no Markdown:

{
  "action": "remove_inverse_pair | merge_rotations | noop",
  "start": integer or null,
  "end": integer or null,
  "parameters": object,
  "reason": string
}

The circuit is represented as an ordered instruction list.
Instruction indexes use Python slicing:
- start is inclusive
- end is exclusive

Allowed actions:

1. remove_inverse_pair

Use only for two adjacent self-inverse operations that:
- have the same operation type;
- act on the same qubit or qubits;
- appear at indexes [start, end);
- have no instruction between them.

Return:

{
  "action": "remove_inverse_pair",
  "start": integer,
  "end": integer,
  "parameters": {
    "gate": "x | y | z | h | cx | cz | swap"
  },
  "reason": "..."
}

2. merge_rotations

Use only for two adjacent single-qubit rotations that:
- are both rx, both ry, or both rz;
- act on the same qubit;
- appear at indexes [start, end);
- have no instruction between them.

The resulting rotation has the sum of the two angles.

Return:

{
  "action": "merge_rotations",
  "start": integer,
  "end": integer,
  "parameters": {
    "axis": "rx | ry | rz"
  },
  "reason": "..."
}

3. noop

Use when no safe local rewrite is visible or when uncertain.

Return:

{
  "action": "noop",
  "start": null,
  "end": null,
  "parameters": {},
  "reason": "..."
}

Rules:
- Do not rewrite the complete circuit.
- Do not change the number of qubits or classical bits.
- Do not invent instruction indexes or qubits.
- Return noop if uncertain.
"""

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                ChatCompletionSystemMessageParam(
                    content=system,
                    role="system",
                ),
                ChatCompletionUserMessageParam(
                    content=circuit.to_string(),
                    role="user",
                ),
            ],
            response_format=ResponseFormatJSONObject(
                type="json_object",
            ),
            temperature=0.4,
        )

        content = response.choices[0].message.content or ""
        data = json.loads(content)

        return CircuitOptimizationProposalDTO(
            action=RewriteActionEnum(data.get("action", "noop")),
            end=data.get("end"),
            parameters=data.get("parameters") or {},
            reason=data.get("reason", ""),
            start=data.get("start"),
        )

    def propose_qasm(self, circuit: str) -> str | None:
            system = """
You are a quantum-circuit optimization assistant.

Inspect the supplied circuit and propose at most one local
rewrite. The rewrite must preserve the circuit's behavior.

Provide a quantum circuit in valid QASM 3.0 code.

Rules:
- Do not change the number of qubits.
- Do not invent qubits.
    """

            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    ChatCompletionSystemMessageParam(
                        content=system,
                        role="system",
                    ),
                    ChatCompletionUserMessageParam(
                        content=circuit,
                        role="user",
                    ),
                ],
                temperature=0.2,
            )

            self._logger.info(f"response: {response.model_dump()}")

            return response.choices[0].message.content or None
