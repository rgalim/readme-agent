import unittest
from unittest.mock import patch

from agent.nodes import clone_repo_node, select_essential_files_node, readme_file_node, readme_body_node
from agent.prompts import get_essential_files_prompt_template, generate_readme_prompt_template


class TestCloneRepoNode(unittest.TestCase):
    def setUp(self):
        """Initial state setup"""
        self.initial_state = {
            "repo_url": "https://github.com/user/repo.git",
            "temp_directory_path": None,
            "file_paths": [],
            "essential_file_names": ["foo.txt"],
            "readme_body": "Initial readme"
        }

    @patch("agent.nodes.get_file_paths")
    @patch("agent.nodes.create_temp_directory")
    @patch("agent.nodes.github_client.clone_repo")
    def test_clone_repo_node_success(self, mock_clone_repo, mock_create_tmp, mock_get_paths):
        """Test successful clone repo"""
        mock_create_tmp.return_value = "/tmp/testdir"
        mock_get_paths.return_value = ["file1.py", "file2.md"]
        state = dict(self.initial_state)

        result = clone_repo_node(state)

        mock_create_tmp.assert_called_once()
        self.assertEqual(result["temp_directory_path"], "/tmp/testdir")

        mock_clone_repo.assert_called_once_with(
            repo_url=self.initial_state["repo_url"],
            target_dir="/tmp/testdir"
        )

        mock_get_paths.assert_called_once_with(repo_path="/tmp/testdir")
        self.assertEqual(result["file_paths"], ["file1.py", "file2.md"])

        self.assertEqual(result["essential_file_names"], self.initial_state["essential_file_names"])
        self.assertEqual(result["readme_body"], self.initial_state["readme_body"])

    @patch("agent.nodes.create_temp_directory")
    @patch("agent.nodes.github_client.clone_repo", side_effect=Exception("clone failed"))
    def test_clone_repo_node_clone_failure_propagates(self, mock_clone_repo, mock_create_tmp):
        """Test clone repo with exception"""
        mock_create_tmp.return_value = "/tmp/faildir"
        state = {"repo_url": "https://github.com/user/repo.git"}

        with self.assertRaises(Exception) as cm:
            clone_repo_node(state)
        self.assertEqual(str(cm.exception), "clone failed")

        mock_create_tmp.assert_called_once()
        mock_clone_repo.assert_called_once()


class TestSelectEssentialFilesNode(unittest.TestCase):
    @patch("agent.nodes.extract_file_names")
    @patch("agent.nodes.llm_client.invoke")
    @patch("agent.nodes.get_file_names")
    def test_select_essential_files_node_success(
        self,
        mock_get_file_names,
        mock_llm_invoke,
        mock_extract_file_names,
    ):
        """Test successful essential files selection"""
        file_paths = ["src/main.py", "CHANGELOG.md"]
        state = {"file_paths": file_paths}
        file_names = ["main.py", "CHANGELOG.md"]
        mock_get_file_names.return_value = file_names

        result_str = '```json\n["main.py"]\n```'
        mock_llm_invoke.return_value = result_str

        essential_names = ["main.py"]
        mock_extract_file_names.return_value = essential_names

        expected_prompt = get_essential_files_prompt_template.format(files=file_names)

        new_state = select_essential_files_node(state)

        mock_get_file_names.assert_called_once_with(file_paths=file_paths)

        mock_llm_invoke.assert_called_once_with(prompt=expected_prompt)

        mock_extract_file_names.assert_called_once_with(string_input=result_str)

        self.assertIn("essential_file_names", new_state)
        self.assertEqual(new_state["essential_file_names"], essential_names)

    @patch("agent.nodes.extract_file_names")
    @patch("agent.nodes.llm_client.invoke")
    @patch("agent.nodes.get_file_names")
    def test_select_essential_files_node_empty_result(
        self,
        mock_get_file_names,
        mock_llm_invoke,
        mock_extract_file_names,
    ):
        """Test essential files selection with empty result"""
        file_paths = []
        state = {"file_paths": file_paths}
        mock_get_file_names.return_value = []

        result_str = "not a json list"
        mock_llm_invoke.return_value = result_str

        mock_extract_file_names.return_value = []

        expected_prompt = get_essential_files_prompt_template.format(files=[])

        new_state = select_essential_files_node(state)

        mock_get_file_names.assert_called_once_with(file_paths=file_paths)
        mock_llm_invoke.assert_called_once_with(prompt=expected_prompt)
        mock_extract_file_names.assert_called_once_with(string_input=result_str)

        self.assertEqual(new_state["essential_file_names"], [])


class TestReadmeBodyNode(unittest.TestCase):
    @patch("agent.nodes.llm_client.invoke")
    @patch("agent.nodes.merge_files")
    @patch("agent.nodes.get_essential_file_paths")
    def test_readme_body_node_success(
        self,
        mock_get_essential_paths,
        mock_merge_files,
        mock_llm_invoke,
    ):
        """Test successful readme body node creation"""
        state = {
            "essential_file_names": ["file1.txt", "file2.md"],
            "file_paths": ["repo/file1.txt", "repo/file2.md", "repo/file3.py"]
        }
        essential_paths = ["repo/file1.txt", "repo/file2.md"]
        mock_get_essential_paths.return_value = essential_paths

        merged_content = "Content of file1 and file2"
        mock_merge_files.return_value = merged_content

        expected_prompt = generate_readme_prompt_template.format(
            all_files_content=merged_content
        )
        generated_readme = "This is the generated README"
        mock_llm_invoke.return_value = generated_readme

        new_state = readme_body_node(state)

        mock_get_essential_paths.assert_called_once_with(
            file_names=state["essential_file_names"],
            file_paths=state["file_paths"]
        )

        mock_merge_files.assert_called_once_with(essential_paths)
        mock_llm_invoke.assert_called_once_with(prompt=expected_prompt)

        self.assertIn("readme_body", new_state)
        self.assertEqual(new_state["readme_body"], generated_readme)

    @patch("agent.nodes.llm_client.invoke")
    @patch("agent.nodes.merge_files")
    @patch("agent.nodes.get_essential_file_paths")
    def test_readme_body_node_empty_essential_files(
        self,
        mock_get_essential_paths,
        mock_merge_files,
        mock_llm_invoke,
    ):
        """Test readme body node creation with empty essential files"""
        state = {
            "essential_file_names": [],
            "file_paths": ["repo/file1.txt", "repo/file2.md"]
        }
        mock_get_essential_paths.return_value = []
        mock_merge_files.return_value = ""

        expected_prompt = generate_readme_prompt_template.format(
            all_files_content=""
        )
        mock_llm_invoke.return_value = ""

        new_state = readme_body_node(state)

        mock_get_essential_paths.assert_called_once_with(
            file_names=[],
            file_paths=state["file_paths"]
        )
        mock_merge_files.assert_called_once_with([])
        mock_llm_invoke.assert_called_once_with(prompt=expected_prompt)

        self.assertEqual(new_state["readme_body"], "")


class TestReadmeFileNode(unittest.TestCase):
    @patch("agent.nodes.create_readme")
    def test_readme_file_node_success(self, mock_create_readme):
        """Test successful readme file creation"""
        state = {
            "readme_body": "Generated README contents",
            "temp_directory_path": "/tmp/testdir"
        }

        result = readme_file_node(state)

        mock_create_readme.assert_called_once_with(
            content="Generated README contents",
            target_dir="/tmp/testdir"
        )
        self.assertIs(result, state)

    @patch("agent.nodes.create_readme")
    def test_readme_file_node_empty_body(self, mock_create_readme):
        """Test readme file creation with empty body"""
        state = {
            "readme_body": "",
            "temp_directory_path": "/tmp/empty"
        }

        result = readme_file_node(state)

        mock_create_readme.assert_called_once_with(
            content="",
            target_dir="/tmp/empty"
        )
        self.assertIs(result, state)