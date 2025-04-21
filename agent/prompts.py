generate_readme_prompt_template = """
    You are an expert in software documentation and code analysis. 
    I am providing you with the contents of several files from a github project. 
    Analyze these files and generate a comprehensive README file that includes:
        - A project overview
        - Installation instructions
        - Usage examples
        - Details on configuration and key components extracted from the source code

    The files provided are:
    {all_files_content}

    Generate a well-structured and detailed README file. Do not include changelog, licence, and contributing sections.
    """

get_essential_files_prompt_template = """
    You are an expert in creating software documentation. 
    Given the following repository file names, identify the essential files 
    that would contribute the most useful information to write a README file.
    Format the output list of the files as an array of strings. For example: ["User.java", "UserController.java"] 

    Repository files: 
    {files}
    """