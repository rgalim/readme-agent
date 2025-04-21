import os

from typing import TypedDict
from dotenv import load_dotenv
from agent.github_client import GitHubClient
from agent.file_utils import create_temp_directory, extract_file_names, merge_files, create_readme, get_file_paths, \
    get_file_names, get_essential_file_paths
from agent.llm_client import LLMClient
from agent.prompts import get_essential_files_prompt_template, generate_readme_prompt_template

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

github_client = GitHubClient(github_token=GITHUB_TOKEN)
llm_client = LLMClient(api_key=OPENAI_API_KEY)


class AgentState(TypedDict):
    repo_url: str
    temp_directory_path: str
    file_paths: list
    essential_file_names: list
    readme_body: str


def clone_repo_node(state: AgentState) -> AgentState:
    temp_directory = create_temp_directory()
    state["temp_directory_path"] = temp_directory
    repo_url = state["repo_url"]

    github_client.clone_repo(repo_url=repo_url, target_dir=temp_directory)

    file_paths = get_file_paths(repo_path=temp_directory)
    state["file_paths"] = file_paths

    return state


def select_essential_files_node(state: AgentState) -> AgentState:
    file_paths = state["file_paths"]
    file_names = get_file_names(file_paths=file_paths)

    prompt = get_essential_files_prompt_template.format(files=file_names)

    result = llm_client.invoke(prompt=prompt)
    essential_file_names = extract_file_names(string_input=result)

    state["essential_file_names"] = essential_file_names
    return state


def readme_body_node(state: AgentState) -> AgentState:
    essential_file_names = state["essential_file_names"]
    file_paths = state["file_paths"]
    essential_file_paths = get_essential_file_paths(file_names=essential_file_names, file_paths=file_paths)

    merged_content = merge_files(essential_file_paths)

    prompt = generate_readme_prompt_template.format(all_files_content=merged_content)

    readme_body = llm_client.invoke(prompt=prompt)

    state["readme_body"] = readme_body

    return state


def readme_file_node(state: AgentState) -> AgentState:
    readme_body = state["readme_body"]
    temp_directory_path = state["temp_directory_path"]

    create_readme(content=readme_body, target_dir=temp_directory_path)

    return state
