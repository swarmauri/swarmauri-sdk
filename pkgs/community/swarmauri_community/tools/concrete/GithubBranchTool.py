# swarmauri/community/tools/concrete/GithubCommunityTool.py

from github import Github, GithubException
from typing import List, Dict, Literal, Optional, Any
from pydantic import Field, ConfigDict
from swarmauri.tools.base.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter


class GithubBranchTool(ToolBase):
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
                name="branch_name",
                type="string",
                description="The name of the branch to interact with.",
                required=False,
            ),
            Parameter(
                name="source_branch",
                type="string",
                description="The name of the source branch to create a branch from.",
                required=False,
            ),
        ]
    )
    name: str = "GithubBranchTool"
    description: str = "Interacts with GitHub branches using PyGithub."
    type: Literal["GithubBranchTool"] = "GithubBranchTool"
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
            "create_branch": self.create_branch,
            "delete_branch": self.delete_branch,
            "list_branches": self.list_branches,
            "get_branch": self.get_branch,
        }

        if action in action_map:
            self._github = Github(self.token)
            return {action: action_map[action](**kwargs)}

        raise ValueError(f"Action '{action}' is not supported.")


    # Branch Management Methods
    def create_branch(
        self, repo_name: str, branch_name: str, source: str = "main"
    ) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            source_branch = repo.get_branch(source)
            repo.create_git_ref(
                ref=f"refs/heads/{branch_name}", sha=source_branch.commit.sha
            )
            return f"Branch '{branch_name}' created successfully."
        except GithubException as e:
            return f"Error creating branch: {e}"

    def delete_branch(self, repo_name: str, branch_name: str) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            ref = repo.get_git_ref(f"heads/{branch_name}")
            ref.delete()
            return f"Branch '{branch_name}' deleted successfully."
        except GithubException as e:
            return f"Error deleting branch: {e}"

    def list_branches(self, repo_name: str) -> List[str]:
        try:
            repo = self._github.get_repo(repo_name)
            return [branch.name for branch in repo.get_branches()]
        except GithubException as e:
            return f"Error listing branches: {e}"

    def get_branch(self, repo_name: str, branch_name: str) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            branch = repo.get_branch(branch_name)
            return f"Branch {branch.name}: {branch.commit.sha}"
        except GithubException as e:
            return f"Error retrieving branch: {e}"

