import os
from pathlib import Path
import sys

import qiskit

from q_rewrite.clients import ModelClient
from q_rewrite.tools import QiskitParser
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
    qasm = qiskit.qasm3.loads(file_path.read_text(encoding="utf-8"))
    summarized_circuit = QiskitParser().summarize(qasm)

    logger.info(f"summarized circuit: {summarized_circuit.to_string()}")

    result = client.propose(summarized_circuit)

    logger.info(f"response: {result}")

if __name__ == "__main__":
    load_env_file(project_root_path=Path(__file__).parent)

    example_path = Path(sys.argv[1] or "")

    if example_path is None:
        raise Exception("qasm file not provided")

    main(file_path=example_path)
