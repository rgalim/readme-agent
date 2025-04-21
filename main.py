import argparse

from langgraph.graph import StateGraph, START, END
from agent.nodes import AgentState, clone_repo_node, select_essential_files_node, readme_body_node, readme_file_node


def build_graph():
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("clone_repo_node", clone_repo_node)
    graph_builder.add_node("select_essential_files_node", select_essential_files_node)
    graph_builder.add_node("readme_body_node", readme_body_node)
    graph_builder.add_node("readme_file_node", readme_file_node)

    graph_builder.add_edge(START, "clone_repo_node")
    graph_builder.add_edge("clone_repo_node", "select_essential_files_node")
    graph_builder.add_edge("select_essential_files_node", "readme_body_node")
    graph_builder.add_edge("readme_body_node", "readme_file_node")
    graph_builder.add_edge("readme_file_node", END)

    return graph_builder.compile()


def get_repo_url():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="URL of the github repo")
    return parser.parse_args().url


def run_agent():
    initial_state = AgentState(
        repo_url=get_repo_url(),
        temp_directory_path="",
        file_paths=[],
        essential_file_names=[],
        readme_body=""
    )

    graph = build_graph()

    graph.invoke(initial_state)


if __name__ == '__main__':
    run_agent()
