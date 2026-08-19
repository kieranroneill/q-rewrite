import json
import logging

from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
from openai.types.shared_params import ResponseFormatJSONObject

from q_rewrite.dtos import CircuitProposalDTO
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
            base_url=base_url,
            api_key=api_key,
        )
        self._logger = logger or get_logger()
        self._model = model

    def model(self):
        return self._model

    def propose(self, qasm: str) -> CircuitProposalDTO:
        system = """
You are a quantum-circuit optimization assistant.

You will be given:
- A QASM 3.0 circuit as text.
- Optional metadata (e.g., gate counts, depth, backend coupling map).

Your task:
- Inspect the supplied QASM 3.0 circuit.
- Propose at most one local, semantics-preserving rewrite.
- The rewrite must:
  - Be small and local (affecting only a few adjacent instructions).
  - Preserve the circuit’s behavior up to global phase.
  - Not change the algorithmic structure (e.g., do not replace a QAOA ansatz
    with a completely different circuit).

Allowed kinds of rewrites (non-exhaustive, examples only):
- Remove adjacent inverse-gate pairs on the same qubit(s), for example:
  - x q[0]; x q[0];
  - h q[0]; h q[0];
  - rz(theta) q[1]; rz(-theta) q[1];
  - rx(theta) q[0]; rx(-theta) q[0];
  - ry(theta) q[0]; ry(-theta) q[0];
- Merge consecutive rotations on the same qubit and axis.
- Remove redundant gate sequences that are known to be identity.
- Simplify known patterns (e.g. certain controlled-gate cancellations).
- Other small, obviously equivalence-preserving local simplifications.

You must NOT:
- Delete only part of an inverse pair (e.g. remove one of two X gates, or one
  of two RZ gates with opposite angles). If you remove an inverse pair, you
  must remove BOTH gates.
- Reorder gates unless the reordering is trivially justified by commutation
  on disjoint qubits and you explicitly state this in the reason.
- Move gates across other gates in a nontrivial way.
- Change control-target relationships unless the transformation is a standard,
  well-known identity and you clearly describe it.
- Replace large subcircuits with structurally different implementations.
- Add or remove qubits or classical bits.
- Add or remove custom gates or instructions not already present.
- Add comments, change whitespace significantly, or otherwise modify the circuit
  beyond the single local rewrite.

Output format:
- Return exactly one JSON object.
- Do not include any Markdown, code fences, explanations, or extra text.
- The JSON must have this exact shape:

{
  "qasm": "<full QASM 3.0 circuit text after applying the rewrite>",
  "reason": "<short explanation of what was changed and why it is valid>"
}

Rules for the "qasm" field:
- It must be valid QASM 3.0.
- It must contain the entire circuit after the proposed rewrite.
- Do not change:
    - The number of qubits.
    - The number of classical bits.
    - The declared registers or their sizes.
    - The order of any gates not directly involved in the rewrite, except where
      strictly required by the rewrite and clearly explained in "reason".

Rules for the "reason" field:
- 1–3 sentences.
- Clearly state:
    - Which gates (by type, parameters, and qubit indices) are affected.
    - What transformation is applied (e.g. “removed two adjacent X gates on q[0]”,
      “removed rz(0.25) q[1] and rz(-0.25) q[1] because they form an inverse pair”).
    - Why this preserves behavior (cite the identity or property used, e.g.
      “X·X = I”, “Rz(θ)·Rz(-θ) = I”, “rotations add”, etc.).
- Explain briefly why no safe local rewrite was found (e.g. “No adjacent
    inverse-gate pairs or other obvious local identities were found.”).
- Do not claim changes that did not take place.

Never claim correctness beyond “preserves behavior up to global phase”;
correctness will be checked by an external verifier.
"""
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                ChatCompletionSystemMessageParam(
                    content=system,
                    role="system",
                ),
                ChatCompletionUserMessageParam(
                    content=qasm,
                    role="user",
                ),
            ],
            response_format=ResponseFormatJSONObject(
                type="json_object",
            ),
            stream=False,
            temperature=0.2,
        )

        content = response.choices[0].message.content or ""
        data = json.loads(content)

        return CircuitProposalDTO(
            qasm=data.get("qasm", qasm),
            reason=data.get("reason", "failed to parse response, returning original circuit"),
        )
