# swarmauri/standard/tools/concrete/GithubTool.py

from github import Github, GithubException
from typing import List, Dict, Literal, Optional, Any
from pydantic import Field, ConfigDict
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter


class GithubLabelTool(ToolBase):
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
                name="label_name",
                type="string",
                description="The name of the label to interact with.",
                required=False,
            ),
            Parameter(
                name="color",
                type="string",
                description="The color of the label to create.",
                required=False,
            ),
            Parameter(
                name="description",
                type="string",
                description="The description of the label to create.",
                required=False,
            ),
        ]
    )
    name: str = "GithubLabelTool"
    description: str = "Interacts with GitHub repositories using PyGithub."
    type: Literal["GithubLabelTool"] = "GithubLabelTool"
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
            "create_label": self.create_label,
            "delete_label": self.delete_label,
            "update_label": self.update_label,
            "list_labels": self.list_labels,
            "get_label": self.get_label,
        }

        if action in action_map:
            self._github = Github(self.token)
            return {action: action_map[action](**kwargs)}

        raise ValueError(f"Action '{action}' is not supported.")

    # Label Management Methods
    def create_label(
        self,
        repo_name: str,
        label_name: str,
        color: str,
        description: Optional[str] = None,
    ) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            label = repo.create_label(
                name=label_name, color=color, description=description
            )
            return f"Label '{label_name}' created successfully."
        except GithubException as e:
            return f"Error creating label: {e}"

    def delete_label(self, repo_name: str, label_name: str) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            label = repo.get_label(name=label_name)
            label.delete()
            return f"Label '{label_name}' deleted successfully."
        except GithubException as e:
            return f"Error deleting label: {e}"

    def update_label(
        self,
        repo_name: str,
        label_name: str,
        new_name: Optional[str] = None,
        color: Optional[str] = None,
        description: Optional[str] = None,
    ) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            label = repo.get_label(name=label_name)
            label.edit(
                name=new_name or label_name,
                color=color or label.color,
                description=description or label.description,
            )
            return f"Label '{label_name}' updated successfully."
        except GithubException as e:
            return f"Error updating label: {e}"

    def list_labels(self, repo_name: str) -> List[str]:
        try:
            repo = self._github.get_repo(repo_name)
            return [label.name for label in repo.get_labels()]
        except GithubException as e:
            return f"Error listing labels: {e}"

    def get_label(self, repo_name: str, label_name: str) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            label = repo.get_label(name=label_name)
            return f"Label {label.name}: {label.color}\n{label.description}"
        except GithubException as e:
            return f"Error retrieving label: {e}"
