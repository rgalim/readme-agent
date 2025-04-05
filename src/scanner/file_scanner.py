import os
import logging

from src.scanner.config import BUILD_FILES, CONFIG_FILES, DOCKER_FILES, EXTRA_FILES

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def select_essential_files(repo_path: str) -> list:
    """
    Traverses the given repository directory and returns a list of file paths that are essential
    for analyzing a Java Spring Boot project for the purpose of creating a README file.

    Essential files include:
      - Build configuration files: pom.xml, build.gradle, build.gradle.kts.
      - Configuration files: application.properties, application.yml (typically in src/main/resources).
      - Docker-related files: Dockerfile, docker-compose.yml.
      - Documentation or meta files: LICENSE, CHANGELOG.md, CONTRIBUTING.md.
      - All .java files for detailed context about what the application is doing.

    Args:
        repo_path (str): The file system path to the local project repository.

    Returns:
        list: A list of absolute paths to the selected files.
    """

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

            if file.endswith(".java"):
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
