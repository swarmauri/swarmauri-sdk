# swarmauri/standard/tools/concrete/GithubTool.py

from github import Github, GithubException
from typing import List, Dict, Literal, Optional, Any
from pydantic import Field, ConfigDict
from swarmauri.tools.base.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter


class GithubCommitTool(ToolBase):
    version: str = "1.1.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="action",
                type="string",
                description="The action to perform on the GitHub API, e.g., 'create_repo', 'delete_repo', 'create_issue', etc.",
                required=True,
            ),
            Parameter(
                name="repo_name",
                type="string",
                description="The full name of the repository to interact with, e.g. 'owner/repository'.",
                required=True,
            ),
            Parameter(
                name="file_path",
                type="string",
                description="The path to the file in the repository, e.g. 'path/to/file.txt'.",
                required=False,
            ),
            Parameter(
                name="message",
                type="string",
                description=".",
                required=False,
            ),
            Parameter(
                name="content",
                type="string",
                description="The name of the branch to interact with.",
                required=False,
            ),
            Parameter(
                name="branch_name",
                type="string",
                description="The name of the branch to interact with.",
                required=False,
            ),
            Parameter(
                name="sha",
                type="string",
                description="The sha of the commit to interact with.",
                required=False,
            ),
            Parameter(
                name="base",
                type="string",
                description="The base of the commit to interact with.",
                required=False,
            ),
            Parameter(
                name="head",
                type="string",
                description="The head of the commit to interact with.",
                required=False,
            ),
        ]
    )
    name: str = "GithubCommitTool"
    description: str = "Interacts with GitHub repositories using PyGithub to submit commits."
    type: Literal["GithubCommitTool"] = "GithubCommitTool"
    token: str
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __call__(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Central method to call various GitHub API actions.

        Args:
            action (str): The action to perform.
            **kwargs: Additional keyword arguments related to the action.

        Returns:
            Dict[str, Any]: The result of the action.
        """
        action_map = {
            "create_commit": self.create_commit,
            "list_commits": self.list_commits,
            "get_commit": self.get_commit,
            "compare_commits": self.compare_commits
        }

        if action in action_map:
            self._github = Github(self.token)
            return {action: action_map[action](**kwargs)}

        raise ValueError(f"Action '{action}' is not supported.")


    # Commit Management Methods
    def create_commit(
        self,
        repo_name: str,
        file_path: str,
        message: str,
        content: str,
        branch: str = "main",
    ) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            repo.create_file(path=file_path, message=message, content=content, branch=branch)
            return f"Commit created successfully at {file_path}."
        except GithubException as e:
            return f"Error creating commit: {e}"

    def list_commits(self, repo_name: str) -> List[str]:
        try:
            repo = self._github.get_repo(repo_name)
            return [commit.commit.message for commit in repo.get_commits()]
        except GithubException as e:
            return f"Error listing commits: {e}"

    def get_commit(self, repo_name: str, sha: str) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            commit = repo.get_commit(sha=sha)
            return f"Commit {commit.sha}: {commit.commit.message}"
        except GithubException as e:
            return f"Error retrieving commit: {e}"

    def compare_commits(self, repo_name: str, base: str, head: str) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            comparison = repo.compare(base, head)
            return f"Comparison from {base} to {head}:\n{comparison.diff_url}"
        except GithubException as e:
            return f"Error comparing commits: {e}"

