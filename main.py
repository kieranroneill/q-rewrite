import os
from pathlib import Path
import sys

import qiskit

from q_rewrite.clients import ModelClient
from q_rewrite.parsers import QiskitParser
from q_rewrite.utilities.logging import get_logger
from q_rewrite.utilities.os import load_env_file

def main(file_path: Path) -> None:
    logger = get_logger()
    client = ModelClient(
        api_key=os.environ["MODEL_API_KEY"],
        base_url=os.environ["MODEL_API_BASE_URL"],
        logger=logger,
        model=os.environ["MODEL"],
    )
    qasm = file_path.read_text(encoding="utf-8")
    circuit = qiskit.qasm3.loads(qasm)
    model_circuit = QiskitParser.from_qiskit_circuit(circuit)
    result = client.propose(model_circuit.circuit())

    logger.info(f"result: {result}")

if __name__ == "__main__":
    load_env_file(project_root_path=Path(__file__).parent)

    example_path = Path(sys.argv[1] or "")

    if example_path is None:
        raise Exception("qasm file not provided")

    main(file_path=example_path)
