import logging

from git import Repo, GitCommandError

HTTPS_PREFIX = "https://"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class GitHubClient:
    def __init__(self, github_token: str):
        self.github_token = github_token

    def clone_repo(self, repo_url: str, target_dir: str) -> None:
        """
        Clones github repo to target directory
        :param repo_url: github repo url
        :param target_dir: path for target directory
        """
        if self.github_token and repo_url.startswith(HTTPS_PREFIX):
            repo_url = self._modify_url(repo_url, self.github_token)
        else:
            raise Exception("Github token is empty or repo url is invalid")

        try:
            Repo.clone_from(repo_url, target_dir)
            logger.info(f"Repository cloned successfully into '{target_dir}'")
        except GitCommandError as e:
            logger.error(f"Error cloning repository: {e}")
            raise

    def _modify_url(self, url: str, token: str) -> str:
        """
        Modifies github url with access token
        :param url: github repo url
        :param token: github access token
        :return: modified url
        """
        return f"{HTTPS_PREFIX}{token}@{url[len(HTTPS_PREFIX):]}"
