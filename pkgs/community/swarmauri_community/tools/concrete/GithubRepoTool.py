# swarmauri/standard/tools/concrete/GithubTool.py

from github import Github, GithubException
from typing import List, Dict, Literal, Any
from pydantic import Field, ConfigDict
from swarmauri.tools.base.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter


class GithubRepoTool(ToolBase):
    version: str = "1.1.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="action",
                type="string",
                description="The action to perform on the GitHub API, e.g., 'create_repo', 'delete_repo', 'update_repo', and 'get_repo'",
                required=True,
            ),
            Parameter(
                name="repo_name",
                type="string",
                description="The full name of the repository to interact with, e.g. 'owner/repository'.",
                required=False,
            ),
            Parameter(
                name="file_path",
                type="string",
                description="The path to the file in the repository, e.g. 'path/to/file.txt'.",
                required=False,
            ),
        ]
    )
    name: str = "GithubRepoTool"
    description: str = "Interacts with GitHub repositories using PyGithub."
    type: Literal["GithubRepoTool"] = "GithubRepoTool"
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
            "create_repo": self.create_repo,
            "delete_repo": self.delete_repo,
            "get_repo": self.get_repo,
            "list_repos": self.list_repos,
            "update_repo": self.update_repo,
        }

        if action in action_map:
            self._github = Github(self.token)
            return {action: action_map[action](**kwargs)}

        raise ValueError(f"Action '{action}' is not supported.")

    # Repository Management Methods
    def create_repo(self, repo_name: str, private: bool = False) -> str:
        try:
            user = self._github.get_user()
            repo = user.create_repo(repo_name, private=private)
            return f"Repository '{repo_name}' created successfully."
        except GithubException as e:
            return f"Error creating repository: {e}"

    def delete_repo(self, repo_name: str) -> str:
        try:
            user = self._github.get_user()
            repo = user.get_repo(repo_name)
            repo.delete()
            return f"Repository '{repo_name}' deleted successfully."
        except GithubException as e:
            return f"Error deleting repository: {e}"

    def get_repo(self, repo_name: str) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            repo_info = f"Repository: {repo.full_name}\nDescription: {repo.description}\nClone URL: {repo.clone_url}"
            return repo_info
        except GithubException as e:
            return f"Error retrieving repository info: {e}"

    def list_repos(self) -> List[str]:
        try:
            user = self._github.get_user()
            return [repo.full_name for repo in user.get_repos()]
        except GithubException as e:
            return f"Error listing repositories: {e}"

    def update_repo(self, repo_name: str, **kwargs) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            repo.edit(**kwargs)
            return f"Repository '{repo_name}' updated successfully."
        except GithubException as e:
            return f"Error updating repository: {e}"
