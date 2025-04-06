import tiktoken


def analyze_files(path: str):
    # TODO: implement integration with LangChain?
    return ""


def count_tokens(text: str, model_name: str) -> int:
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(text))
