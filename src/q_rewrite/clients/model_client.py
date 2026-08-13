import json
import logging

from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
from openai.types.shared_params import ResponseFormatJSONObject

from q_rewrite.dtos import CircuitSummaryDTO, ProposalCircuitDTO
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

    def propose(self, circuit_summary: CircuitSummaryDTO) -> ProposalCircuitDTO:
        system = """
You optimize quantum circuits using only local, semantics-preserving rewrites.

Return exactly one JSON object:
{
  "action": "remove_inverse_pair | merge_rotations | noop",
  "start": integer or null,
  "end": integer or null,
  "reason": string
}

Rules:
- Return only JSON.
- Use instruction indexes from the input.
- Never invent qubit indexes.
- Do not propose a rewrite unless it is locally valid.
- Use noop if no safe rewrite is visible.
"""

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                ChatCompletionSystemMessageParam(
                    content=system,
                    role="system",
                ),
                ChatCompletionUserMessageParam(
                    content=circuit_summary.to_string(),
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

        return ProposalCircuitDTO(
            action=data.get("action", "noop"),
            end=data.get("end"),
            reason=data.get("reason", ""),
            start=data.get("start"),
        )

    def propose_qasm(self, circuit: str) -> str | None:
            system = """
You are a quantum circuit optimization agent.
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
