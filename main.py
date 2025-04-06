import logging

from src.github.repo_manager import clone_repo, create_temp_directory, create_readme
from src.llm.prompt_manager import count_tokens, create_prompt
from src.scanner.file_scanner import select_essential_files, merge_files
from src.llm.config import MODEL_NAME, INPUT_TOKEN_LIMIT, TEMPERATURE
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def run():
    repository_url = ""
    access_token = ""
    openai_api_key = ""

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
    prompt = create_prompt(merged_content)

    # 7. Send prompt to LLM
    llm = ChatOpenAI(model=MODEL_NAME, temperature=TEMPERATURE, api_key=openai_api_key)
    response = llm.invoke([HumanMessage(content=prompt)])

    # 8. Create a readme file
    create_readme(response.content, temp_directory)


if __name__ == '__main__':
    run()
