import logging
import os
import tempfile

from git import Repo, GitCommandError

HTTPS_PREFIX = "https://"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def create_temp_directory() -> str:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    temp_base_dir = os.path.join(project_root, ".temp")

    os.makedirs(temp_base_dir, exist_ok=True)

    temp_dir = tempfile.mkdtemp(dir=temp_base_dir)
    logger.info(f"Temporary directory created at: {temp_dir}")
    return temp_dir


def clone_repo(repo_url: str, target_dir: str, token: str = None) -> None:

    if token and repo_url.startswith("https://"):
        repo_url = _modify_url(repo_url, token)

    try:
        Repo.clone_from(repo_url, target_dir)
        logger.info(f"Repository cloned successfully into '{target_dir}'")
    except GitCommandError as e:
        logger.error(f"Error cloning repository: {e}")
        raise


def create_readme(content: str, target_dir: str) -> None:
    try:
        file_path = os.path.join(target_dir, "README.md")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        logger.info("README.md file created successfully.")
    except Exception as e:
        logger.error(f"Error creating README: {e}")


def _modify_url(url: str, token: str) -> str:
    return f"{HTTPS_PREFIX}{token}@{url[len(HTTPS_PREFIX):]}"
