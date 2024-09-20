# swarmauri/standard/tools/concrete/GithubTool.py

from github import Github, GithubException
from typing import List, Dict, Literal, Optional, Any
from pydantic import Field, ConfigDict
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter


class GithubCollaboratorTool(ToolBase):
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
                required=False,
            ),
            Parameter(
                name="username",
                type="string",
                description="The GitHub username for collaborator management.",
                required=False,
            ),
            Parameter(
                name="permission",
                type="string",
                description="The permission level for the collaborator.",
                required=False,
                default="push",
            ),
        ]
    )
    name: str = "GithubCollaboratorTool"
    description: str = "Interacts with GitHub repositories using PyGithub."
    type: Literal["GithubCollaboratorTool"] = "GithubCollaboratorTool"
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
            "add_collaborator": self.add_collaborator,
            "remove_collaborator": self.remove_collaborator,
            "list_collaborators": self.list_collaborators,
            "check_collaborator": self.check_collaborator,
        }

        if action in action_map:
            self._github = Github(self.token)
            return {action: action_map[action](**kwargs)}

        raise ValueError(f"Action '{action}' is not supported.")

    # Collaborator Management Methods
    def add_collaborator(
        self, repo_name: str, username: str, permission: str = "push"
    ) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            repo.add_to_collaborators(username, permission)
            return f"Collaborator '{username}' added successfully with '{permission}' permission."
        except GithubException as e:
            return f"Error adding collaborator: {e}"

    def remove_collaborator(self, repo_name: str, username: str) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            repo.remove_from_collaborators(username)
            return f"Collaborator '{username}' removed successfully."
        except GithubException as e:
            return f"Error removing collaborator: {e}"

    def list_collaborators(self, repo_name: str) -> List[str]:
        try:
            repo = self._github.get_repo(repo_name)
            return [collaborator.login for collaborator in repo.get_collaborators()]
        except GithubException as e:
            return f"Error listing collaborators: {e}"

    def check_collaborator(self, repo_name: str, username: str) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            if repo.has_in_collaborators(username):
                return f"User '{username}' is a collaborator."
            else:
                return f"User '{username}' is not a collaborator."
        except GithubException as e:
            return f"Error checking collaborator status: {e}"
