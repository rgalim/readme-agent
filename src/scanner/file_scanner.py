import os
import logging

from src.scanner.config import BUILD_FILES, CONFIG_FILES, DOCKER_FILES, EXTRA_FILES

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def select_essential_files(repo_path: str) -> list:
    essential_files = set()

    for root, dirs, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)

            if file in BUILD_FILES:
                essential_files.add(file_path)

            if file in CONFIG_FILES and os.path.join("src", "main", "resources") in root:
                essential_files.add(file_path)

            if file in DOCKER_FILES:
                essential_files.add(file_path)

            if file in EXTRA_FILES:
                essential_files.add(file_path)

            if file.endswith(".java") and not file.endswith("Test.java"):
                essential_files.add(file_path)

    return sorted(essential_files)


def merge_files(file_paths: list) -> str:
    all_files_content = ""
    for path in file_paths:
        try:
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
                filename = os.path.basename(path)
                all_files_content += f"--- {filename} ---\n{content}\n\n"
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
    return all_files_content
