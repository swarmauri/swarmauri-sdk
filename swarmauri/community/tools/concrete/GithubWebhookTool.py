# swarmauri/standard/tools/concrete/GithubTool.py

from github import Github, GithubException
from typing import List, Dict, Literal, Optional, Any
from pydantic import Field, ConfigDict
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter


class GithubWebhookTool(ToolBase):
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
                name="webhook_id",
                type="integer",
                description="The ID of the webhook to interact with.",
                required=False,
            ),
            Parameter(
                name="config",
                type="dict",
                description="The configuration for the webhook.",
                required=False,
            ),
            Parameter(
                name="events",
                type="list",
                description="The events the webhook should listen to.",
                required=False,
            ),
            Parameter(
                name="active",
                type="boolean",
                description="Whether the webhook should be active.",
                required=False,
                default=False,
            ),
        ]
    )
    name: str = "GithubWebhookTool"
    description: str = "Interacts with GitHub repositories using PyGithub."
    type: Literal["GithubWebhookTool"] = "GithubWebhookTool"
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
            "create_webhook": self.create_webhook,
            "delete_webhook": self.delete_webhook,
            "list_webhooks": self.list_webhooks,
            "get_webhook": self.get_webhook,
        }

        if action in action_map:
            self._github = Github(self.token)
            return {action: action_map[action](**kwargs)}

        raise ValueError(f"Action '{action}' is not supported.")

    # Webhook Management Methods
    def create_webhook(
        self,
        repo_name: str,
        config: Dict[str, str],
        events: List[str],
        active: bool = True,
    ) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            webhook = repo.create_hook(
                name="web", config=config, events=events, active=active
            )
            return f"Webhook created successfully with ID {webhook.id}."
        except GithubException as e:
            return f"Error creating webhook: {e}"

    def delete_webhook(self, repo_name: str, hook_id: int) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            hook = repo.get_hook(hook_id)
            hook.delete()
            return f"Webhook with ID {hook_id} deleted successfully."
        except GithubException as e:
            return f"Error deleting webhook: {e}"

    def list_webhooks(self, repo_name: str) -> List[str]:
        try:
            repo = self._github.get_repo(repo_name)
            return [
                f"Webhook {hook.id}: {hook.config['url']}" for hook in repo.get_hooks()
            ]
        except GithubException as e:
            return f"Error listing webhooks: {e}"

    def get_webhook(self, repo_name: str, hook_id: int) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            hook = repo.get_hook(hook_id)
            return f"Webhook {hook.id}: {hook.config['url']}\nEvents: {hook.events}\nActive: {hook.active}"
        except GithubException as e:
            return f"Error retrieving webhook: {e}"
