import tiktoken


def create_prompt(all_files_content: str) -> str:
    return f"""
        You are an expert in software documentation and code analysis. 
        I am providing you with the contents of several files from a Java project. 
        Analyze these files and generate a comprehensive README file that includes:
            - A project overview
            - Installation instructions
            - Usage examples
            - Details on configuration and key components extracted from the source code

        The files provided are:
        {all_files_content}
        
        Generate a well-structured and detailed README file. Do not include changelog, licence, and contributing sections.
    """


def count_tokens(text: str, model_name: str) -> int:
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(text))
