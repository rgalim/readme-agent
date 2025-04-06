import logging

from src.github.repo_manager import clone_repo, create_temp_directory
from src.llm.file_analyzer import count_tokens
from src.scanner.file_scanner import select_essential_files, merge_files
from src.llm.config import MODEL_NAME, INPUT_TOKEN_LIMIT

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def run():
    repository_url = ""
    access_token = ""

    # 1. Create temp directory
    temp_directory = create_temp_directory()

    # 2. Clone repo from provided url
    clone_repo(repository_url, temp_directory, token=access_token)

    # 3. Select essential project files (only java is supported)
    files = select_essential_files(temp_directory)

    # 4. Merge all files content
    merged_content = merge_files(files)

    # 5. Calculate tokens
    token_count = count_tokens(text=merged_content, model_name=MODEL_NAME)
    logger.info(f"NUMBER OF TOKENS: {token_count}")

    if token_count > INPUT_TOKEN_LIMIT:
        logger.info(f"Prompt exceeds token limit: {token_count}")
        raise Exception("Prompt exceeds token limit")

    # 6. Create a prompt
    # 7. Send prompt to LLM
    # 8. Create a readme file


if __name__ == '__main__':
    run()
