import json
import logging

from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
from openai.types.shared_params import ResponseFormatJSONObject

from q_rewrite.canonical_graph.graph_builder import GraphBuilder
from q_rewrite.dtos import CircuitProposalDTO
from q_rewrite.utilities.logging import get_logger

class ModelClientGraph:
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

    def propose(self, qasm: str) -> CircuitProposalDTO:
        graph_builder = GraphBuilder()
        graph = graph_builder.build_canonical_graph(qasm)
        serialized_graph = graph_builder.serialize_graph_for_llm(graph)
        print(serialized_graph)

        system = ["""
SYSTEM PROMPT:
CRITICAL CANCELLATION RULES:
1. CANCEL CONDITION: Two gates CAN ONLY cancel if they meet ALL of these conditions:
   a. They are the EXACT SAME gate type (e.g., X and X, RZ and RZ). NEVER mix types.
   b. They act on the EXACT SAME qubit(s).
   c. They are self-inverse OR parameterized gates whose angles sum to 0.
   d. There are NO directed dependency edges blocking them.
2. NEVER delete a gate simply because it commutes.

You MUST output your analysis in this exact JSON format, following the steps sequentially:
{
  "step_1_read_nodes": [
    "List every node ID and its gate type and qubit here to prove you read them"
  ],
  "step_2_evaluate_pairs": [
    {
      "node_A_id": "ID",
      "node_A_gate": "Gate Type",
      "node_B_id": "ID",
      "node_B_gate": "Gate Type",
      "qubits": "Qubits they act on",
      "are_gates_identical": true/false,
      "blocking_edges_exist": true/false,
      "do_they_cancel": true/false
    }
  ],
  "nodes_to_delete": [List IDs ONLY for pairs where do_they_cancel is true]
}

USER PROMPT:

=== EXAMPLE TASK ===
Input Graph:
 - Node 98: Z on [2]
 - Node 99: X on [0]
 - Node 100: Z on [2]
Dependencies: (None)

Expected Output JSON:
{
  "step_1_read_nodes": [
    "Node 98 is Z on [2]",
    "Node 99 is X on [0]",
    "Node 100 is Z on [2]"
  ],
  "step_2_evaluate_pairs": [
    {
      "node_A_id": 98,
      "node_A_gate": "Z",
      "node_B_id": 100,
      "node_B_gate": "Z",
      "qubits": "[2]",
      "are_gates_identical": true,
      "blocking_edges_exist": false,
      "do_they_cancel": true
    }
  ],
  "nodes_to_delete": [98, 100]
}

=== YOUR ACTUAL TASK ===

\n === ORIGINAL QASM === \n """ + qasm + """
\n === CANONICAL GRAPH === \n """ + serialized_graph + """\n

Analyze the graph using the CRITICAL CANCELLATION RULES. If a valid pair exists, output its nodes in "nodes_to_delete". If no valid pair exists, output "nodes_to_delete": [].

"""]
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                ChatCompletionSystemMessageParam(
                    content=system[0],
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
            temperature=0.0,
        )

        content = response.choices[0].message.content or ""
        print(content)
        updated_qasm = graph_builder.rebuild_qasm_without_nodes(qasm, json.loads(content)["nodes_to_delete"])
        print(updated_qasm)
        print(json.loads(content)["nodes_to_delete"])
        print(json.loads(content))

