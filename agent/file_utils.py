import logging
import os
import tempfile
import json
import re

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def create_temp_directory() -> str:
    """
    Creates temp directory
    :return: temp directory path
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    temp_base_dir = os.path.join(project_root, ".temp")

    os.makedirs(temp_base_dir, exist_ok=True)

    temp_dir = tempfile.mkdtemp(dir=temp_base_dir)
    logger.info(f"Temporary directory created at: {temp_dir}")
    return temp_dir


def get_file_paths(repo_path: str) -> list:
    """
    Gets absolute file paths from provided repo
    :param repo_path: path of the repo
    :return: list of file paths
    """
    file_paths = set()

    for root, dirs, files in os.walk(repo_path):
        if '.git' in dirs:
            dirs.remove('.git')

        for file in files:
            if not file == '.gitignore':
                file_path = os.path.join(root, file)
                file_paths.add(file_path)

    return sorted(file_paths)


def get_file_names(file_paths: list) -> list:
    """
    Gets file names from file paths
    :param file_paths: list of absolute file paths
    :return: list of file names
    """
    file_names = []

    for path in file_paths:
        filename = path.split('/')[-1]
        file_names.append(filename)

    return file_names


def get_essential_file_paths(file_names: list, file_paths: list) -> list:
    """
    Gets essential file paths that match provided file names
    :param file_names: list of file names
    :param file_paths: list of absolute file paths
    :return: filtered list of file paths
    """
    essential_file_paths = []

    for path in file_paths:
        filename = path.split('/')[-1]

        if filename in file_names:
            essential_file_paths.append(path)

    return essential_file_paths


def create_readme(content: str, target_dir: str) -> None:
    """
    Creates readme file from string description in provided repo
    :param content: readme file content
    :param target_dir: path for target repo
    """
    try:
        file_path = os.path.join(target_dir, "README.md")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        logger.info("README.md file created successfully.")
    except Exception as e:
        logger.error(f"Error creating README: {e}")


def merge_files(file_paths: list) -> str:
    """
    Merges files content into string
    :param file_paths: list of absolute file paths
    :return: merged file content
    """
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


def extract_file_names(string_input) -> list:
    """
    Extracts file names from LLM response
    :param string_input: LLM response
    :return: list of essential file names
    """
    # Extract the content between square brackets
    match = re.search(r'\[(.*?)\]', string_input)
    if not match:
        return []
    json_content = "[" + match.group(1) + "]"
    try:
        return json.loads(json_content)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing file names: {e}")
        return []
