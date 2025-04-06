import os
import io
import pytest

from src.scanner.file_scanner import select_essential_files, merge_files

BUILD_FILES = {"pom.xml", "build.gradle"}
CONFIG_FILES = {"application.properties", "application.yml"}
EXTRA_FILES = {"CHANGELOG.md"}
DOCKER_FILES = {"Dockerfile"}


def mock_os_walk(repo_path):
    return [
        ("/repo", ["src", "other"], [
            "build.gradle",
            "CHANGELOG.md",
            "random.java",
            "Test.java",
            "ExampleTest.java",
            "Example.java",
        ]),
        ("/repo/src/main/resources", [], [
            "application.properties",
            "config.yaml",
            "extra.txt"
        ]),
        ("/repo/other", [], [
            "Dockerfile",
            "pom.xml",
            "irrelevant.txt"
        ])
    ]


def mock_join(*args):
    return "/".join(args)


def mock_open_factory(file_contents: dict):
    def fake_open(path, mode="r", encoding=None):
        if path in file_contents:
            return io.StringIO(file_contents[path])
        raise FileNotFoundError(f"File not found: {path}")

    return fake_open


@pytest.fixture(autouse=True)
def patch_os(monkeypatch):
    monkeypatch.setattr(os, "walk", mock_os_walk)
    monkeypatch.setattr(os.path, "join", mock_join)


@pytest.fixture(autouse=True)
def patch_constants(monkeypatch):
    import src.scanner.file_scanner as module_under_test
    monkeypatch.setattr(module_under_test, "BUILD_FILES", BUILD_FILES)
    monkeypatch.setattr(module_under_test, "CONFIG_FILES", CONFIG_FILES)
    monkeypatch.setattr(module_under_test, "DOCKER_FILES", DOCKER_FILES)
    monkeypatch.setattr(module_under_test, "EXTRA_FILES", EXTRA_FILES)


def test_select_essential_files():
    result = select_essential_files("/repo")

    expected = {
        "/repo/build.gradle",
        "/repo/CHANGELOG.md",
        "/repo/random.java",
        "/repo/Example.java",
        "/repo/src/main/resources/application.properties",
        "/repo/other/Dockerfile",
        "/repo/other/pom.xml"
    }

    assert result == sorted(expected)


def test_empty_repo(monkeypatch):
    monkeypatch.setattr(os, "walk", lambda repo: [])
    result = select_essential_files("/empty_repo")
    assert result == []


def test_merge_files_all_success(monkeypatch):
    file_contents = {
        "file1.txt": "Content of file 1",
        "file2.txt": "Content of file 2"
    }
    monkeypatch.setattr("builtins.open", mock_open_factory(file_contents))

    result = merge_files(["file1.txt", "file2.txt"])

    expected = (
        "--- file1.txt ---\nContent of file 1\n\n"
        "--- file2.txt ---\nContent of file 2\n\n"
    )
    assert result == expected


def test_merge_files_with_error(monkeypatch, caplog):
    file_contents = {
        "file1.txt": "Content of file 1",
        "file2.txt": "Content of file 2"
    }
    monkeypatch.setattr("builtins.open", mock_open_factory(file_contents))

    result = merge_files(["file1.txt", "bad.txt", "file2.txt"])

    expected = (
        "--- file1.txt ---\nContent of file 1\n\n"
        "--- file2.txt ---\nContent of file 2\n\n"
    )
    assert result == expected

    assert "Error reading file bad.txt:" in caplog.text


def test_merge_files_empty():
    result = merge_files([])
    assert result == ""
