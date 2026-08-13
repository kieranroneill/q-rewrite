from pathlib import Path

from dotenv import load_dotenv


def load_env_file(project_root_path: Path, env_file_path: Path | None = None) -> None:
    """
    Loads the .env file. If no .env file exists, it defaults to the .env.dev file.

    An optional `env_file_path` maybe passed to override.

    Args:
        project_root_path: The project root path.
        env_file_path: [optional] An .env file path. Defaults to None.
    """
    _env_file_path = Path(project_root_path / ".env.dev")

    # if the .env file exists, this takes precedence over the .env.dev
    if Path(project_root_path / ".env").exists():
        _env_file_path = Path(project_root_path / ".env")

    if env_file_path is not None and env_file_path.exists():
        _env_file_path = env_file_path

    load_dotenv(_env_file_path)
