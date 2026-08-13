import os
from pathlib import Path
import subprocess

from q_rewrite.utilities.logging import get_logger
from utilities import load_env_file


PROJECT_ROOT_PATH = Path(__file__).parent.parent

def main() -> int:
    """
    Starts the model locally via Docker.

    The model is determined from the "OLLAMA_MODEL" environment variable defined in the `.env` file, if it exists,
    otherwise it defaults to the env vars in the `.env.dev` file.`

    Examples:
        python start_model.py

    Returns:
        Exit code 0 on success, or 1 if there was an error.
    """
    logger = get_logger()

    if os.environ.get("OLLAMA_MODEL") is None:
        logger.error('env var "OLLAMA_MODEL" is not set')

        return 1

    compose_file_path = PROJECT_ROOT_PATH / "deployments" / "compose.development.yml"

    logger.info(f'starting model "{os.environ["OLLAMA_MODEL"]}" in docker')

    # run the docker compose
    result = subprocess.run(
        [
            "docker",
            "compose",
            "-f", str(compose_file_path),
            "-p", "q-rewrite-dev",
            "up",
            "--build"
        ],
        cwd=PROJECT_ROOT_PATH
    )

    return result.returncode


if __name__ == "__main__":
    load_env_file(project_root_path=PROJECT_ROOT_PATH)

    main()
