from __future__ import annotations

import numpy as np
from qiskit.qasm3 import loads as loads_qasm3
from qiskit.quantum_info import Operator

from .base_verifier import BaseVerifier


class QiskitVerifier(BaseVerifier):
    def equivalence(
        self,
        candidate_circuit: str,
        reference_circuit: str,
    ) -> bool:
        """
        Check whether two circuits are unitary-equivalent up to global-phase.

        This method computes the full unitary matrix for each circuit and compares them, allowing for a global phase
        difference. Measurements are removed before comparison, as they are not part of the unitary.

        **NOTE**: The check is exact up to numerical tolerance and is feasible only for relatively small circuits due to
        the exponential cost of constructing the full unitary.

        Args:
            candidate_circuit (str): The candidate circuit, in QASM 3.0 format.
            reference_circuit (str): The reference circuit, in QASM 3.0 format used to compare.

        Returns:
            bool: True if the circuits are equivalent up to global-phase, False otherwise.

        Raises:
            Exception: If unitary construction or comparison fails (for example, due to unsupported operations or
            excessive circuit size).
        """
        _candidate_circuit = loads_qasm3(candidate_circuit)
        _reference_circuit = loads_qasm3(reference_circuit)

        if _reference_circuit.num_qubits != _candidate_circuit.num_qubits:
            return False

        lhs = _reference_circuit.remove_final_measurements(inplace=False)
        rhs = _candidate_circuit.remove_final_measurements(inplace=False)

        if lhs is None or rhs is None:
            raise Exception("failed to remove measurements")

        reference_operator = Operator(lhs).data
        candidate_operator = Operator(rhs).data

        overlap = np.vdot(
            reference_operator.flatten(),
            candidate_operator.flatten(),
        )

        if abs(overlap) < 1e-12:
            return False

        phase = overlap / abs(overlap)

        return np.allclose(
            reference_operator,
            phase * candidate_operator,
            atol=1e-8,
            rtol=1e-8,
        )

