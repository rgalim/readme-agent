import os
import shutil
import pytest
from git import GitCommandError

from src.github.repo_manager import create_temp_directory, clone_repo, create_readme


class MockFile:
    def __init__(self):
        self.content = ""

    def write(self, s):
        self.content += s

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


def test_create_temp_directory():
    temp_dir = create_temp_directory()

    assert os.path.exists(temp_dir)

    parent_dir = os.path.basename(os.path.dirname(temp_dir))
    assert parent_dir == ".temp"

    shutil.rmtree(temp_dir)


@pytest.fixture(autouse=True)
def reset_recorder():
    _clone_from_recorder.called = False
    _clone_from_recorder.called_with = None
    yield


def test_clone_repository_success_with_token(monkeypatch):
    monkeypatch.setattr("src.github.repo_manager.Repo.clone_from", _clone_from_recorder)

    repo_url = "https://github.com/user/repo.git"
    target_dir = "/.temp/path"
    token = "token"
    expected_url = "https://token@github.com/user/repo.git"

    clone_repo(repo_url, target_dir, token=token)

    assert _clone_from_recorder.called
    called_url, called_target = _clone_from_recorder.called_with
    assert called_url == expected_url
    assert called_target == target_dir


def test_clone_repository_success_without_token(monkeypatch):
    monkeypatch.setattr("src.github.repo_manager.Repo.clone_from", _clone_from_recorder)

    repo_url = "https://github.com/user/repo.git"
    target_dir = "/.temp/path"
    token = None

    clone_repo(repo_url, target_dir, token=token)

    assert _clone_from_recorder.called
    called_url, called_target = _clone_from_recorder.called_with
    assert called_url == repo_url
    assert called_target == target_dir


def test_clone_repository_failure(monkeypatch):
    monkeypatch.setattr("src.github.repo_manager.Repo.clone_from", _clone_from_failure)

    repo_url = "https://github.com/user/repo.git"
    target_dir = "/.temp/path"
    token = "token"

    with pytest.raises(GitCommandError):
        clone_repo(repo_url, target_dir, token=token)


def test_create_readme_success(monkeypatch):
    files_written = {}

    def mock_open(path, mode, encoding):
        mock_file = MockFile()
        files_written[path] = mock_file
        return mock_file

    monkeypatch.setattr("builtins.open", mock_open)

    target_dir = "/mock_dir"
    content = "This is a test README content."

    create_readme(content, target_dir)

    expected_path = os.path.join(target_dir, "README.md")

    assert expected_path in files_written
    assert files_written[expected_path].content == content


def test_create_readme_failure(monkeypatch, caplog):
    def mock_open_fail(path, mode, encoding):
        raise Exception("Simulated file write error")

    monkeypatch.setattr("builtins.open", mock_open_fail)

    target_dir = "/fake_dir"
    content = "This is a test README content."

    create_readme(content, target_dir)

    assert "Error creating README:" in caplog.text


def _clone_from_recorder(url, target_dir):
    _clone_from_recorder.called = True
    _clone_from_recorder.called_with = (url, target_dir)


def _clone_from_failure(url, target_dir):
    raise GitCommandError("clone", "clone error")
