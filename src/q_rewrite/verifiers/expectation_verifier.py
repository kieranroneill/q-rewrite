from __future__ import annotations

from qiskit import QuantumCircuit, transpile
from qiskit.primitives import ObservablesArrayLike
from qiskit_aer.primitives import EstimatorV2
from qiskit.qasm3 import loads as loads_qasm3

from q_rewrite.dtos.verification_dto import VerificationDTO
from q_rewrite.dtos.verification_resource_dto import VerificationResourceDTO

from .base_verifier import BaseVerifier
from q_rewrite.utilities.logging import get_logger

class ExpectationVerifier(BaseVerifier):

    """"
    This class implements a verification strategy of circuit equivalency as suggested by 
    paper : https://arxiv.org/pdf/2504.11109. Though the paper suggests to use circuit based
    Hamiltonians, this class uses simple hamlitonians based on Pauli Gates.
    """

    expectation_difference_tolerance = 0.05

    @classmethod
    def equivalence(
        cls,
        candidate_circuit: str,
        reference_circuit: str, 
    ) -> bool:
        """
        Check whether two circuits are unitary-equivalent upto a threshold.

        This method calculates the expectation of the unitary, representing
        the circuit and returns True if the difference between the two expectations
        is less than a 0.05.
        
        Args:
            candidate_circuit (str): The candidate circuit, in QASM 3.0 format.
            reference_circuit (str): The reference circuit, in QASM 3.0 format used to compare.

        Returns:
            bool: True if the circuits are equivalent up to global-phase, False otherwise.
        
        """

        _candidate_circuit = loads_qasm3(candidate_circuit)
        _reference_circuit = loads_qasm3(reference_circuit)
    
        if _reference_circuit.num_qubits != _candidate_circuit.num_qubits:
            return False
        
        estimator = EstimatorV2()

        basic_observables = ['X', 'Y', 'Z']
        primitive_unified_blocks = []

        for observable in basic_observables:
            n_qubit_observable = ''
            for _ in range(0, _reference_circuit.num_qubits):
                n_qubit_observable += observable
            primitive_unified_blocks.append((transpile(_reference_circuit), n_qubit_observable))
            primitive_unified_blocks.append((transpile(_candidate_circuit), n_qubit_observable))

        job = estimator.run(primitive_unified_blocks)
        results = job.result()

        for i in range(0, len(results), 2):
            reference_ev = results[i].data.evs
            candidate_ev = results[i+1].data.evs
            if (abs(reference_ev - candidate_ev) > cls.expectation_difference_tolerance):
                get_logger().debug(f"""Expectation difference above tolerance level : reference circuit expectation : 
                                   ${reference_ev} and candidate circuit expectation : ${candidate_ev}""")
                return False
            
        return True

