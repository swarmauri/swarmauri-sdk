# swarmauri/standard/tools/concrete/GithubTool.py

from github import Github, GithubException
from typing import List, Dict, Literal, Optional, Any
from pydantic import Field, ConfigDict
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter


class GithubGistTool(ToolBase):
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
                name="gist_id",
                type="string",
                description="The ID of the gist to interact with.",
                required=False,
            ),
            Parameter(
                name="files",
                type="dict",
                description="The files to interact with.",
                required=False,
            ),
            Parameter(
                name="description",
                type="string",
                description="The description of the gist to create.",
                required=False,
            ),
            Parameter(
                name="public",
                type="boolean",
                description="Whether the gist should be public.",
                required=False,
                default=True,
            ),
        ]
    )
    name: str = "GithubGistTool"
    description: str = "Interacts with GitHub repositories using PyGithub."
    type: Literal["GithubGistTool"] = "GithubGistTool"
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
            "create_gist": self.create_gist,
            "delete_gist": self.delete_gist,
            "update_gist": self.update_gist,
            "list_gists": self.list_gists,
            "get_gist": self.get_gist,
        }

        if action in action_map:
            self._github = Github(self.token)
            return {action: action_map[action](**kwargs)}

        raise ValueError(f"Action '{action}' is not supported.")

    # Gist Management Methods
    def create_gist(
        self, files: Dict[str, str], description: str = "", public: bool = True
    ) -> str:
        try:
            gist = self._github.get_user().create_gist(
                public=public, files=files, description=description
            )
            return f"Gist created successfully with ID {gist.id}."
        except GithubException as e:
            return f"Error creating gist: {e}"

    def delete_gist(self, gist_id: str) -> str:
        try:
            gist = self._github.get_gist(gist_id)
            gist.delete()
            return f"Gist with ID {gist_id} deleted successfully."
        except GithubException as e:
            return f"Error deleting gist: {e}"

    def update_gist(
        self,
        gist_id: str,
        files: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
    ) -> str:
        try:
            gist = self._github.get_gist(gist_id)
            gist.edit(files=files, description=description)
            return f"Gist with ID {gist_id} updated successfully."
        except GithubException as e:
            return f"Error updating gist: {e}"

    def list_gists(self) -> List[str]:
        try:
            return [gist.id for gist in self._github.get_user().get_gists()]
        except GithubException as e:
            return f"Error listing gists: {e}"

    def get_gist(self, gist_id: str) -> str:
        try:
            gist = self._github.get_gist(gist_id)
            files = "\n".join(
                [
                    f"{fname}: {fileinfo['raw_url']}"
                    for fname, fileinfo in gist.files.items()
                ]
            )
            return f"Gist {gist.id}: {gist.description}\nFiles: \n{files}"
        except GithubException as e:
            return f"Error retrieving gist: {e}"
