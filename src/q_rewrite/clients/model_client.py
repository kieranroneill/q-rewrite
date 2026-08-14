import json
import logging

from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
from openai.types.shared_params import ResponseFormatJSONObject

from q_rewrite.dtos import ModelCircuitDTO, ModelCircuitProposalDTO
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

    def propose(self, circuit: ModelCircuitDTO) -> ModelCircuitProposalDTO:
        system = """
You are a quantum-circuit optimization assistant.

Inspect the supplied circuit summary and propose at most one local
rewrite. The rewrite must preserve the circuit's behavior.

Return exactly one JSON object and no Markdown:

{
  "action": "remove_inverse_pair | merge_rotations | noop",
  "start": integer or null,
  "end": integer or null,
  "reason": string
}

The circuit is represented as an ordered instruction list.
Instruction indexes use Python slicing:
- start is inclusive
- end is exclusive

Inspect adjacent instructions and look for a safe local simplification.

Use:
- remove_inverse_pair for two adjacent operations that undo one another;
- merge_rotations for compatible adjacent rotations on the same qubit;
- noop when no safe local simplification is apparent.

Rules:
- Do not rewrite the complete circuit.
- Do not change the number of qubits.
- Do not invent instruction indexes or qubits.
- Do not propose a transformation that depends on gates being non-adjacent.
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
            temperature=0.2,
        )

        self._logger.info(f"response: {response.model_dump()}")

        content = response.choices[0].message.content or ""
        data = json.loads(content)

        return ModelCircuitProposalDTO(
            action=data.get("action", "noop"),
            end=data.get("end"),
            reason=data.get("reason", ""),
            start=data.get("start"),
        )

    def propose_qasm(self, circuit: str) -> str | None:
            system = """
You are a helpful quantum circuit design assistant. Provide a
quantum circuit in valid QASM 3.0 code with optimal gate parameters
so that the output state encodes the solution, ensuring that the
measurement outcomes have a high probability of reflecting the
correct answer.
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
