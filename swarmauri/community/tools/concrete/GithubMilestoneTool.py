# swarmauri/standard/tools/concrete/GithubTool.py

from github import Github, GithubException
from typing import List, Dict, Literal, Optional, Any
from pydantic import Field, ConfigDict
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter


class GithubMilestoneTool(ToolBase):
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
                name="milestone_number",
                type="integer",
                description="The number of the milestone to interact with.",
                required=False,
            ),
            Parameter(
                name="title",
                type="string",
                description="The title of the milestone to create.",
                required=False,
            ),
            Parameter(
                name="description",
                type="string",
                description="The description of the milestone to create.",
                required=False,
            ),
            Parameter(
                name="state",
                type="string",
                description="The state of the milestone to create.",
                required=False,
            ),
        ]
    )
    name: str = "GithubMilestoneTool"
    description: str = "Interacts with GitHub repositories using PyGithub."
    type: Literal["GithubMilestoneTool"] = "GithubMilestoneTool"
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
            "create_milestone": self.create_milestone,
            "close_milestone": self.close_milestone,
            "update_milestone": self.update_milestone,
            "list_milestones": self.list_milestones,
            "get_milestone": self.get_milestone,
        }

        if action in action_map:
            self._github = Github(self.token)
            return {action: action_map[action](**kwargs)}

        raise ValueError(f"Action '{action}' is not supported.")

    # Milestone Management Methods
    def create_milestone(
        self, repo_name: str, title: str, description: str = None, state: str = "open"
    ) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            milestone = repo.create_milestone(
                title=title, description=description, state=state
            )
            return f"Milestone '{title}' created successfully."
        except GithubException as e:
            return f"Error creating milestone: {e}"

    def close_milestone(self, repo_name: str, milestone_number: int) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            milestone = repo.get_milestone(number=milestone_number)
            milestone.edit(state="closed")
            return f"Milestone '{milestone.title}' closed successfully."
        except GithubException as e:
            return f"Error closing milestone: {e}"

    def update_milestone(self, repo_name: str, milestone_number: int, **kwargs) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            milestone = repo.get_milestone(number=milestone_number)
            milestone.edit(**kwargs)
            return f"Milestone '{milestone.title}' updated successfully."
        except GithubException as e:
            return f"Error updating milestone: {e}"

    def list_milestones(self, repo_name: str) -> List[str]:
        try:
            repo = self._github.get_repo(repo_name)
            return [milestone.title for milestone in repo.get_milestones()]
        except GithubException as e:
            return f"Error listing milestones: {e}"

    def get_milestone(self, repo_name: str, milestone_number: int) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            milestone = repo.get_milestone(number=milestone_number)
            return f"Milestone {milestone.number}: {milestone.title}\n{milestone.description}"
        except GithubException as e:
            return f"Error retrieving milestone: {e}"
