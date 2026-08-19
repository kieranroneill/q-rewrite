import logging
import numpy as np

from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

from q_rewrite.utilities.logging import get_logger
from qiskit.qasm3 import dumps as dumps_qasm3
from qiskit.qasm3 import loads as loads_qasm3
from qiskit.converters import circuit_to_dag, dag_to_dagdependency

class GraphBuilder:
    def __init__(
        self,
        logger: logging.Logger | None = None,
    ):
        self._logger = logger or get_logger()

    def gates_commute(self, gate1, gate2) -> bool:
        """Check if two Qiskit circuit instructions commute."""
        q1 = set(gate1.qubits)
        q2 = set(gate2.qubits)
        if q1.isdisjoint(q2):
            return True
        
        u1 = Operator(gate1.operation).data
        u2 = Operator(gate2.operation).data
        try:
            return np.allclose(u1 @ u2, u2 @ u1)
        except Exception:
            return False

    def build_canonical_graph(self, qasm: str) -> dict:
        """
        Implements Algorithm 1 (Iten et al., 2019) to construct the Canonical Dependency Graph.
        Includes proper predecessor masking to prevent redundant transitive edges.
        """
        qc = loads_qasm3(qasm)
        gates = qc.data
        num_gates = len(gates)
        
        nodes = []
        edges = []
        
        # Dictionary to track all predecessors (ancestors) for each node
        ancestors = {k: set() for k in range(num_gates)}
        
        for idx, inst in enumerate(gates):
            nodes.append({
                "id": idx,
                "gate": inst.operation.name.upper(),
                "qubits": [qc.find_bit(q).index for q in inst.qubits]
            })
        
        for j in range(num_gates):
            is_reachable = [True] * num_gates
            for i in range(j - 1, -1, -1):
                if is_reachable[i] and not self.gates_commute(gates[i], gates[j]):
                    edges.append({"from": i, "to": j})
                    
                    ancestors[j].add(i)
                    ancestors[j].update(ancestors[i])
                    
                    for p in ancestors[i]:
                        is_reachable[p] = False

        return {"nodes": nodes, "edges": edges}
        

    def serialize_graph_for_llm(self, graph_data):
        """Convert canonical graph into clear prompt context for LLMs."""
        text = "=== QUANTUM CIRCUIT CANONICAL GRAPH ===\n"
        text += "GATES (NODES):\n"
        for node in graph_data["nodes"]:
            text += f" - Node {node['id']}: {node['gate']} on qubit(s) {node['qubits']}\n"
        
        text += "\nNON-COMMUTING DEPENDENCIES (DIRECTED EDGES):\n"
        for edge in graph_data["edges"]:
            text += f" - Node {edge['from']} -> Node {edge['to']}\n"
        return text

    def rebuild_qasm_without_nodes(self, original_qasm: str, nodes_to_delete: list[int]) -> str:
        """
        Loads an OPENQASM 3 circuit, removes specified instruction indices,
        and returns the new OPENQASM 3 string.
        """
        qc = loads_qasm3(original_qasm)
        
        delete_set = set(nodes_to_delete)
        
        new_qc = QuantumCircuit(*qc.qregs, *qc.cregs)
        
        for idx, instruction in enumerate(qc.data):
            if idx not in delete_set:
                new_qc.append(instruction)
    
        return dumps_qasm3(new_qc)

