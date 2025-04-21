import unittest
from unittest.mock import patch
from git import GitCommandError

from agent.github_client import GitHubClient, HTTPS_PREFIX


class TestGitHubClient(unittest.TestCase):
    def setUp(self):
        self.token = "token123"
        self.client = GitHubClient(self.token)
        self.valid_url = HTTPS_PREFIX + "github.com/owner/repo.git"
        self.target_dir = "/tmp/clone_target"

    def test__modify_url_injects_token(self):
        """Test url is modified if url contains https prefix"""
        original = self.valid_url
        modified = self.client._modify_url(original, self.token)
        expected = f"{HTTPS_PREFIX}{self.token}@{original[len(HTTPS_PREFIX):]}"

        assert modified == expected

    @patch("agent.github_client.Repo.clone_from")
    def test_clone_repo_success(self, mock_clone):
        """Test the repo is cloned successfully"""
        self.client.clone_repo(self.valid_url, self.target_dir)

        expected_url = self.client._modify_url(self.valid_url, self.token)

        mock_clone.assert_called_once_with(expected_url, self.target_dir)

    def test_clone_repo_invalid_url_raises(self):
        """Test the repo clone with invalid url"""
        bad_url = "git@github.com:owner/repo.git"
        with self.assertRaises(Exception) as ex:
            self.client.clone_repo(bad_url, self.target_dir)
        self.assertIn("Github token is empty or repo url is invalid", str(ex.exception))

    def test_clone_repo_empty_token_raises(self):
        """Test the repo clone with empty token"""
        client_no_token = GitHubClient("")
        with self.assertRaises(Exception) as ex:
            client_no_token.clone_repo(self.valid_url, self.target_dir)
        self.assertIn("Github token is empty or repo url is invalid", str(ex.exception))

    @patch("agent.github_client.Repo.clone_from", side_effect=GitCommandError("clone", "failed"))
    def test_clone_repo_git_error_propagates(self, mock_clone):
        """Test the repo clone with propagated error"""
        with self.assertRaises(GitCommandError):
            self.client.clone_repo(self.valid_url, self.target_dir)
        mock_clone.assert_called_once()
