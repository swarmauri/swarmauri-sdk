# swarmauri/community/tools/concrete/GithubPRTool.py

from github import Github, GithubException
from typing import List, Dict, Literal, Optional, Any
from pydantic import Field, ConfigDict
from swarmauri.tools.base.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter


class GithubPRTool(ToolBase):
    version: str = "1.1.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="action",
                type="string",
                description="The action to perform on the GitHub API, e.g., 'create_pull', 'merge_pull', 'close_pull', 'get_pull', 'list_pulls' etc.",
                required=True,
            ),
            Parameter(
                name="repo_name",
                type="string",
                description="The full name of the repository to interact with, e.g. 'owner/repository'.",
                required=False,
            ),
            Parameter(
                name="pull_number",
                type="integer",
                description="The number of the pull request to interact with.",
                required=False,
            ),
            Parameter(
                name="title",
                type="string",
                description="The title of the pull request to create.",
                required=False,
            ),
            Parameter(
                name="head",
                type="string",
                description="The head branch with your changes",
                required=False,
            ),
            Parameter(
                name="base",
                type="string",
                description="The base branch you're merging into, typically 'main' or 'master'",
                required=False,
            ),
            Parameter(
                name="body",
                type="string",
                description="The description of the pull request to create.",
                required=False,
            ),
        ]
    )
    name: str = "GithubPRTool"
    description: str = "Interacts with GitHub repositories using PyGithub."
    type: Literal["GithubPRTool"] = "GithubPRTool"
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
            "create_pull": self.create_pull,
            "merge_pull": self.merge_pull,
            "close_pull": self.close_pull,
            "list_pulls": self.list_pulls,
            "get_pull": self.get_pull,
        }

        if action in action_map:
            self._github = Github(self.token)
            return {action: action_map[action](**kwargs)}

        raise ValueError(f"Action '{action}' is not supported.")

    # Pull Request Management Methods
    def create_pull(
        self, repo_name: str, title: str, head: str, base: str, body: str = None
    ) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            pull = repo.create_pull(title=title, body=body, head=head, base=base)
            return f"Pull request '{title}' created successfully."
        except GithubException as e:
            return f"Error creating pull request: {e}"

    def merge_pull(self, repo_name: str, pull_number: int) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            pull = repo.get_pull(number=pull_number)
            pull.merge()
            return f"Pull request '{pull_number}' merged successfully."
        except GithubException as e:
            return f"Error merging pull request: {e}"

    def close_pull(self, repo_name: str, pull_number: int) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            pull = repo.get_pull(number=pull_number)
            pull.edit(state="closed")
            return f"Pull request '{pull_number}' closed successfully."
        except GithubException as e:
            return f"Error closing pull request: {e}"

    def list_pulls(self, repo_name: str) -> List[str]:
        try:
            repo = self._github.get_repo(repo_name)
            return [pr.title for pr in repo.get_pulls(state="open")]
        except GithubException as e:
            return f"Error listing pull requests: {e}"

    def get_pull(self, repo_name: str, pull_number: int) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            pull = repo.get_pull(number=pull_number)
            return f"Pull Request #{pull.number}: {pull.title}\n{pull.body}"
        except GithubException as e:
            return f"Error retrieving pull request: {e}"
