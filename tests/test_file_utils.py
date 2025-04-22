import os
import pytest
import tempfile

from unittest.mock import patch, mock_open, MagicMock
from tempfile import TemporaryDirectory

from agent.file_utils import create_temp_directory, get_file_paths, get_file_names, get_essential_file_paths, \
    create_readme, merge_files, extract_file_names


class TestCreateTempDirectory:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.original_mkdtemp = tempfile.mkdtemp

    def teardown_method(self):
        """Tear down test fixtures after each test method."""
        tempfile.mkdtemp = self.original_mkdtemp

    @patch('os.path.dirname')
    @patch('os.path.abspath')
    @patch('os.makedirs')
    @patch('tempfile.mkdtemp')
    def test_creates_correct_directory_structure(self, mock_mkdtemp, mock_makedirs, mock_abspath, mock_dirname):
        """Test that the function creates the correct directory structure."""
        mock_dirname.return_value = '/fake/path/to/module'
        mock_abspath.return_value = '/fake/project/root'
        mock_mkdtemp.return_value = '/fake/project/root/.temp/tmpabcd1234'

        result = create_temp_directory()

        expected_temp_base_dir = '/fake/project/root/.temp'
        mock_makedirs.assert_called_once_with(expected_temp_base_dir, exist_ok=True)
        mock_mkdtemp.assert_called_once_with(dir=expected_temp_base_dir)

        assert result == '/fake/project/root/.temp/tmpabcd1234'

    @patch('os.path.dirname')
    @patch('os.path.abspath')
    @patch('os.makedirs')
    @patch('tempfile.mkdtemp')
    def test_handles_makedirs_errors(self, mock_mkdtemp, mock_makedirs, mock_abspath, mock_dirname):
        """Test that the function handles errors when creating directories."""
        mock_dirname.return_value = '/fake/path/to/module'
        mock_abspath.return_value = '/fake/project/root'
        mock_makedirs.side_effect = PermissionError("Permission denied")

        with pytest.raises(PermissionError):
            create_temp_directory()

        mock_mkdtemp.assert_not_called()

    @patch('os.path.dirname')
    @patch('os.path.abspath')
    @patch('os.makedirs')
    @patch('tempfile.mkdtemp')
    def test_handles_mkdtemp_errors(self, mock_mkdtemp, mock_makedirs, mock_abspath, mock_dirname):
        """Test that the function handles errors when creating the temp directory."""
        mock_dirname.return_value = '/fake/path/to/module'
        mock_abspath.return_value = '/fake/project/root'
        mock_mkdtemp.side_effect = PermissionError("Permission denied")

        with pytest.raises(PermissionError):
            create_temp_directory()

        mock_makedirs.assert_called_once()


class TestGetFilePaths:
    def setup_method(self):
        """Set up test environment before each test"""
        self.temp_dir = TemporaryDirectory()
        self.repo_path = self.temp_dir.name

    def teardown_method(self):
        """Clean up test environment after each test"""
        self.temp_dir.cleanup()

    def create_file_structure(self, structure: dict):
        """
        Helper to create a file structure for testing
        :param structure: Dictionary representing directory structure
                e.g. {'file1.txt': 'content', 'dir1': {'file2.txt': 'content'}}
        """

        def _create_structure(directory, file_structure):
            for name, content in file_structure.items():
                path = os.path.join(directory, name)
                if isinstance(content, dict):
                    os.makedirs(path, exist_ok=True)
                    _create_structure(path, content)
                else:
                    with open(path, 'w') as f:
                        f.write(content)

        _create_structure(self.repo_path, structure)

    def test_empty_directory(self):
        """Test with an empty directory"""
        result = get_file_paths(self.repo_path)
        assert result == []

    def test_single_file(self):
        """Test with a directory containing a single file"""
        self.create_file_structure({'file1.txt': 'content'})
        expected = [os.path.join(self.repo_path, 'file1.txt')]

        result = get_file_paths(self.repo_path)
        assert result == expected

    def test_multiple_files(self):
        """Test with a directory containing multiple files"""
        self.create_file_structure({
            'file1.txt': 'content1',
            'file2.py': 'content2',
            'file3.md': 'content3'
        })

        expected = sorted([
            os.path.join(self.repo_path, 'file1.txt'),
            os.path.join(self.repo_path, 'file2.py'),
            os.path.join(self.repo_path, 'file3.md')
        ])

        result = get_file_paths(self.repo_path)
        assert result == expected

    def test_nested_directory_structure(self):
        """Test with nested directory structure"""
        self.create_file_structure({
            'file1.txt': 'content1',
            'dir1': {
                'file2.py': 'content2',
                'subdir': {
                    'file3.md': 'content3'
                }
            },
            'dir2': {
                'file4.js': 'content4'
            }
        })

        expected = sorted([
            os.path.join(self.repo_path, 'file1.txt'),
            os.path.join(self.repo_path, 'dir1', 'file2.py'),
            os.path.join(self.repo_path, 'dir1', 'subdir', 'file3.md'),
            os.path.join(self.repo_path, 'dir2', 'file4.js')
        ])

        result = get_file_paths(self.repo_path)
        assert result == expected

    def test_gitignore_exclusion(self):
        """Test that .gitignore files are excluded"""
        self.create_file_structure({
            'file1.txt': 'content1',
            '.gitignore': 'ignore patterns',
            'dir1': {
                'file2.py': 'content2',
                '.gitignore': 'more ignore patterns'
            }
        })

        expected = sorted([
            os.path.join(self.repo_path, 'file1.txt'),
            os.path.join(self.repo_path, 'dir1', 'file2.py')
        ])

        result = get_file_paths(self.repo_path)
        assert result == expected

    def test_git_directory_exclusion(self):
        """Test that .git directories are excluded"""
        self.create_file_structure({
            'file1.txt': 'content1',
            '.git': {
                'HEAD': 'ref: refs/heads/main',
                'config': 'git config',
                'objects': {
                    'pack': {
                        'pack1.idx': 'index content'
                    }
                }
            },
            'dir1': {
                'file2.py': 'content2'
            }
        })

        expected = sorted([
            os.path.join(self.repo_path, 'file1.txt'),
            os.path.join(self.repo_path, 'dir1', 'file2.py')
        ])

        result = get_file_paths(self.repo_path)
        assert result == expected

    def test_nonexistent_directory(self):
        """Test with a nonexistent directory"""
        non_existent_path = os.path.join(self.repo_path, "does_not_exist")

        result = get_file_paths(non_existent_path)

        assert result == []

    @patch('os.walk')
    def test_os_walk_mock(self, mock_walk):
        """Test with mocked os.walk to ensure full control over test data"""
        mock_walk.return_value = [
            ('/repo', ['.git', 'src'], ['README.md', '.gitignore']),
            ('/repo/src', [], ['main.py', 'utils.py'])
        ]

        expected = sorted([
            '/repo/README.md',
            '/repo/src/main.py',
            '/repo/src/utils.py'
        ])

        result = get_file_paths('/repo')
        assert result == expected


class TestGetFileNames:
    def test_basic_file_paths(self):
        """Test with basic file paths"""
        file_paths = [
            '/home/user/documents/file1.txt',
            '/home/user/documents/file2.pdf',
            '/home/user/images/image.png'
        ]
        expected = ['file1.txt', 'file2.pdf', 'image.png']

        result = get_file_names(file_paths)
        assert result == expected

    def test_empty_list(self):
        """Test with an empty list of file paths"""
        file_paths = []
        expected = []

        result = get_file_names(file_paths)
        assert result == expected

    def test_paths_with_no_extension(self):
        """Test with file paths that have no file extension"""
        file_paths = [
            '/home/user/documents/file1',
            '/home/user/documents/README',
            '/home/user/bin/executable'
        ]
        expected = ['file1', 'README', 'executable']

        result = get_file_names(file_paths)
        assert result == expected

    def test_hidden_files(self):
        """Test with hidden files"""
        file_paths = [
            '/home/user/.config',
            '/home/user/documents/.hidden_file',
            '/home/user/.ssh/id_rsa'
        ]
        expected = ['.config', '.hidden_file', 'id_rsa']

        result = get_file_names(file_paths)
        assert result == expected


class TestGetEssentialFilePaths:
    def test_basic_filtering(self):
        """Test basic filtering of file paths based on file names"""
        file_names = ['file1.txt', 'file3.txt']
        file_paths = [
            '/home/user/documents/file1.txt',
            '/home/user/documents/file2.txt',
            '/home/user/downloads/file3.txt',
            '/home/user/pictures/file4.jpg'
        ]
        expected = [
            '/home/user/documents/file1.txt',
            '/home/user/downloads/file3.txt'
        ]

        result = get_essential_file_paths(file_names, file_paths)
        assert result == expected

    def test_empty_file_names(self):
        """Test with empty file_names list"""
        file_names = []
        file_paths = [
            '/home/user/documents/file1.txt',
            '/home/user/documents/file2.txt'
        ]
        expected = []

        result = get_essential_file_paths(file_names, file_paths)
        assert result == expected

    def test_empty_file_paths(self):
        """Test with empty file_paths list"""
        file_names = ['file1.txt', 'file2.txt']
        file_paths = []
        expected = []

        result = get_essential_file_paths(file_names, file_paths)
        assert result == expected

    def test_no_matches(self):
        """Test when no file names match the given paths"""
        file_names = ['nonexistent1.txt', 'nonexistent2.txt']
        file_paths = [
            '/home/user/documents/file1.txt',
            '/home/user/documents/file2.txt'
        ]
        expected = []

        result = get_essential_file_paths(file_names, file_paths)
        assert result == expected


class TestCreateReadme:
    def teardown_method(self):
        """Tear down test fixtures after each test method."""
        if hasattr(self, 'test_dir') and os.path.exists(self.test_dir):
            readme_path = os.path.join(self.test_dir, "README.md")
            if os.path.exists(readme_path):
                os.remove(readme_path)
            if os.path.exists(self.test_dir):
                os.rmdir(self.test_dir)

    @patch('builtins.open', new_callable=mock_open)
    def test_creates_readme_with_content(self, mock_file):
        """Test that the function creates a README.md file with the correct content."""
        content = "# Test README\nThis is a test README file."
        target_dir = "/fake/directory"

        create_readme(content, target_dir)

        expected_path = os.path.join(target_dir, "README.md")
        mock_file.assert_called_once_with(expected_path, "w", encoding="utf-8")

        mock_file().write.assert_called_once_with(content)

    @patch('builtins.open', new_callable=mock_open)
    def test_with_empty_content(self, mock_file):
        """Test with empty content."""
        content = ""
        target_dir = "/fake/directory"

        create_readme(content, target_dir)

        expected_path = os.path.join(target_dir, "README.md")
        mock_file.assert_called_once_with(expected_path, "w", encoding="utf-8")

        mock_file().write.assert_called_once_with(content)


class TestMergeFiles:
    @patch('builtins.open')
    @patch('os.path.basename')
    def test_merge_single_file(self, mock_basename, mock_open):
        """Test merging a single file."""
        mock_file = mock_open.return_value.__enter__.return_value
        mock_file.read.return_value = "This is the content of file1."
        mock_basename.return_value = "file1.txt"

        result = merge_files(["/path/to/file1.txt"])

        expected = "--- file1.txt ---\nThis is the content of file1.\n\n"
        assert result == expected

        mock_open.assert_called_once_with("/path/to/file1.txt", "r", encoding="utf-8")
        mock_basename.assert_called_once_with("/path/to/file1.txt")

    @patch('builtins.open')
    @patch('os.path.basename')
    def test_merge_multiple_files(self, mock_basename, mock_open):
        """Test merging multiple files."""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_file.read.side_effect = [
            "Content of file 1.",
            "Content of file 2.",
            "Content of file 3."
        ]
        mock_basename.side_effect = ["file1.txt", "file2.py", "file3.md"]

        result = merge_files(["/path/to/file1.txt", "/path/to/file2.py", "/path/to/file3.md"])

        expected = (
            "--- file1.txt ---\nContent of file 1.\n\n"
            "--- file2.py ---\nContent of file 2.\n\n"
            "--- file3.md ---\nContent of file 3.\n\n"
        )
        assert result == expected

        assert mock_open.call_count == 3

    @patch('builtins.open')
    @patch('os.path.basename')
    def test_empty_file_list(self, mock_basename, mock_open):
        """Test with an empty list of files."""
        result = merge_files([])

        assert result == ""

        mock_open.assert_not_called()
        mock_basename.assert_not_called()

    @patch('builtins.open')
    @patch('os.path.basename')
    def test_empty_file_content(self, mock_basename, mock_open):
        """Test with files that have empty content."""
        mock_file = mock_open.return_value.__enter__.return_value
        mock_file.read.return_value = ""
        mock_basename.return_value = "empty_file.txt"

        result = merge_files(["/path/to/empty_file.txt"])

        expected = "--- empty_file.txt ---\n\n\n"
        assert result == expected

    @patch('builtins.open')
    @patch('os.path.basename')
    def test_file_read_error(self, mock_basename, mock_open):
        """Test handling of file read errors."""
        mock_open.side_effect = [
            IOError("Permission denied"),
            mock_open.return_value
        ]
        mock_file = mock_open.return_value.__enter__.return_value
        mock_file.read.return_value = "Content of file 2."
        mock_basename.return_value = "file2.txt"

        result = merge_files(["/path/to/file1.txt", "/path/to/file2.txt"])

        expected = "--- file2.txt ---\nContent of file 2.\n\n"
        assert result == expected

    @patch('builtins.open')
    @patch('os.path.basename')
    def test_all_files_error(self, mock_basename, mock_open):
        """Test when all files have read errors."""
        mock_open.side_effect = IOError("Permission denied")

        result = merge_files(["/path/to/file1.txt", "/path/to/file2.txt"])

        assert result == ""

    def test_function_does_not_raise_exception(self):
        """Test that the function doesn't raise exceptions even with problematic inputs."""
        nonexistent_path = "/definitely/not/a/real/path/file.txt"
        try:
            result = merge_files([nonexistent_path])

            assert result == ""

        except Exception as e:
            pytest.fail(f"Function raised an exception unexpectedly: {e}")


class TestExtractFileNames:
    def test_valid_json_list(self):
        """Test with valid json list"""
        input_str = '```json \n["file1.txt","file2.doc"]\n```'
        expected = ["file1.txt", "file2.doc"]

        result = extract_file_names(input_str)

        assert result == expected

    def test_no_brackets(self):
        """Test when input has no brackets"""
        input_str = "No brackets here"
        expected = []

        result = extract_file_names(input_str)

        assert result == expected

    def test_empty_brackets(self):
        """Test when input has empty brackets"""
        input_str = '```json \n[]\n```'
        expected = []

        result = extract_file_names(input_str)

        assert result == expected

    def test_another_format_llm_response(self):
        """Test with another llm response format list"""
        input_str = """
            To write a comprehensive README file, the following files would provide the most useful information:

            ```json
            [
                "file1.txt",
                "file2.doc",
            ]
            ```
            These files are likely to contain the main application logic, configuration settings, and change history.
        """
        expected = ["file1.txt", "file2.doc"]

        result = extract_file_names(input_str)

        assert result == expected
