import pytest
from qiskit import QuantumCircuit

from q_rewrite.canonical_graph.graph_builder import GraphBuilder
from qiskit.qasm3 import dumps as dumps_qasm3

@pytest.fixture
def builder():
    return GraphBuilder()

class TestGraphBuilder:
    def test_build_graph_2_qubits_all_noncommuting(self, builder):
        qc = QuantumCircuit(2)
        qc.x(0)
        qc.cx(0, 1)
        qc.x(0)
        qc.cx(0, 1)

        graph = builder.build_canonical_graph(dumps_qasm3(qc))
        # Gates: X, CX, X, CX => 4 nodes
        # Dependencies: X -> CX, CX -> X, X -> CX => 3 edges
        assert len(graph["nodes"]) == 4
        assert len(graph["edges"]) == 3

    def test_build_graph_2_qubits_commuting_and_noncommuting(self, builder):
        qc = QuantumCircuit(2)
        qc.x(0)
        qc.z(1)  # Commuting with the previous X gate
        qc.cx(0, 1)
        qc.x(0)
        qc.cx(0, 1)

        graph = builder.build_canonical_graph(dumps_qasm3(qc))
        # Gates: X, Z, CX, X, CX => 5 nodes
        # Dependencies: X -> CX, Z -> CX,  CX -> X, X -> CX => 4 edges

        print("Graph nodes:", graph["nodes"])
        assert len(graph["nodes"]) == 5
        assert len(graph["edges"]) == 4

    def test_serialize_graph_for_llm(self, builder):
        qc = QuantumCircuit(2)
        qc.x(0)
        qc.cx(0, 1)
        qc.x(0)
        qc.cx(0, 1)

        graph = builder.build_canonical_graph(dumps_qasm3(qc))
        serialized = builder.serialize_graph_for_llm(graph)

        expected_output = """
=== QUANTUM CIRCUIT CANONICAL GRAPH ===
GATES (NODES):
 - Node 0: X on qubit(s) [0]
 - Node 1: CX on qubit(s) [0, 1]
 - Node 2: X on qubit(s) [0]
 - Node 3: CX on qubit(s) [0, 1]

NON-COMMUTING DEPENDENCIES (DIRECTED EDGES):
 - Node 0 -> Node 1
 - Node 1 -> Node 2
 - Node 2 -> Node 3
"""
        assert serialized.strip() == expected_output.strip()