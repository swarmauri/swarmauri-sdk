# swarmauri/standard/tools/concrete/GithubTool.py

from github import Github, GithubException
from typing import List, Dict, Literal, Optional, Any
from pydantic import Field, ConfigDict
from swarmauri.tools.base.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter


class GithubIssueTool(ToolBase):
    version: str = "1.1.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="action",
                type="string",
                description="The action to perform on the GitHub API, e.g., 'create_issue', 'delete_issue', 'close_issue', 'list_issues', 'get_issue'",
                required=True,
            ),
            Parameter(
                name="repo_name",
                type="string",
                description="The full name of the repository to interact with, e.g. 'owner/repository'.",
                required=False,
            ),
            Parameter(
                name="title",
                type="string",
                description="Title of the issue to create",
                required=False,
            ),
            Parameter(
                name="body",
                type="string",
                description="Body of the issue to create",
                required=False,
            ),
            Parameter(
                name="issue_number",
                type="integer",
                description="The number of the issue to interact with.",
                required=False,
            ),
        ]
    )
    name: str = "GithubIssueTool"
    description: str = "Interacts with GitHub repositories using PyGithub."
    type: Literal["GithubIssueTool"] = "GithubIssueTool"
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
            "create_issue": self.create_issue,
            "close_issue": self.close_issue,
            "update_issue": self.update_issue,
            "list_issues": self.list_issues,
            "get_issue": self.get_issue,
        }

        if action in action_map:
            self._github = Github(self.token)
            return {action: action_map[action](**kwargs)}

        raise ValueError(f"Action '{action}' is not supported.")

    # Issue Management Methods
    def create_issue(self, repo_name: str, title: str, body: str = None) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            issue = repo.create_issue(title=title, body=body)
            return f"Issue '{title}' created successfully."
        except GithubException as e:
            return f"Error creating issue: {e}"

    def close_issue(self, repo_name: str, issue_number: int) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            issue = repo.get_issue(number=issue_number)
            issue.edit(state="closed")
            return f"Issue '{issue_number}' closed successfully."
        except GithubException as e:
            return f"Error closing issue: {e}"

    def update_issue(self, repo_name: str, issue_number: int, **kwargs) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            issue = repo.get_issue(number=issue_number)
            issue.edit(**kwargs)
            return f"Issue '{issue_number}' updated successfully."
        except GithubException as e:
            return f"Error updating issue: {e}"

    def list_issues(self, repo_name: str) -> List[str]:
        try:
            repo = self._github.get_repo(repo_name)
            return [issue.title for issue in repo.get_issues(state="open")]
        except GithubException as e:
            return f"Error listing issues: {e}"

    def get_issue(self, repo_name: str, issue_number: int) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            issue = repo.get_issue(number=issue_number)
            return f"Issue #{issue.number}: {issue.title}\n{issue.body}"
        except GithubException as e:
            return f"Error retrieving issue: {e}"
