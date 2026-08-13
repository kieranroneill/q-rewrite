import os
from pathlib import Path
from unittest import result

import qiskit
from qiskit import QuantumCircuit

from q_rewrite.clients import ModelClient
from q_rewrite.tools import QiskitParser
from q_rewrite.utilities.logging import get_logger
from q_rewrite.utilities.os import load_env_file

def main() -> None:
    load_env_file(project_root_path=Path(__file__).parent)

    logger = get_logger()

    circuit = QuantumCircuit(2)

    circuit.h(0)
    circuit.cx(0, 1)

    # these two gates cancel
    circuit.x(0)
    circuit.x(0)

    circuit.cx(0, 1)

    client = ModelClient(
        api_key=os.environ["MODEL_API_KEY"],
        base_url=os.environ["MODEL_API_BASE_URL"],
        logger=logger,
        model=os.environ["MODEL"],
    )
    # summarized_circuit = QiskitParser().summarize(circuit)
    #
    # logger.info(f"summarized circuit: {summarized_circuit.to_string()}")
    #
    # result = client.propose(summarized_circuit)
    #
    # logger.info(f"response: {result}")

    result = client.propose_qasm(qiskit.qasm3.dumps(circuit))

    logger.info(f"result: {result}")

if __name__ == "__main__":
    main()
