# swarmauri/standard/tools/concrete/GithubTool.py

from github import Github, GithubException
from typing import List, Dict, Literal, Optional, Any
from pydantic import Field, ConfigDict
from swarmauri.tools.base.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter


class GithubTool(ToolBase):
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
                name="file_path",
                type="string",
                description="The path to the file in the repository, e.g. 'path/to/file.txt'.",
                required=False,
            ),
            Parameter(
                name="issue_number",
                type="integer",
                description="The number of the issue to interact with.",
                required=False,
            ),
            Parameter(
                name="pull_number",
                type="integer",
                description="The number of the pull request to interact with.",
                required=False,
            ),
            Parameter(
                name="branch_name",
                type="string",
                description="The name of the branch to interact with.",
                required=False,
            ),
            Parameter(
                name="username",
                type="string",
                description="The GitHub username for collaborator management.",
                required=False,
            ),
            Parameter(
                name="milestone_number",
                type="integer",
                description="The number of the milestone to interact with.",
                required=False,
            ),
            Parameter(
                name="label_name",
                type="string",
                description="The name of the label to interact with.",
                required=False,
            ),
            Parameter(
                name="webhook_id",
                type="integer",
                description="The ID of the webhook to interact with.",
                required=False,
            ),
            Parameter(
                name="gist_id",
                type="string",
                description="The ID of the gist to interact with.",
                required=False,
            ),
        ]
    )
    name: str = "GithubTool"
    description: str = "Interacts with GitHub repositories using PyGithub."
    type: Literal["GithubTool"] = "GithubTool"
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
            "create_issue": self.create_issue,
            "close_issue": self.close_issue,
            "update_issue": self.update_issue,
            "list_issues": self.list_issues,
            "get_issue": self.get_issue,
            "create_pull": self.create_pull,
            "merge_pull": self.merge_pull,
            "close_pull": self.close_pull,
            "list_pulls": self.list_pulls,
            "get_pull": self.get_pull,
            "create_commit": self.create_commit,
            "list_commits": self.list_commits,
            "get_commit": self.get_commit,
            "compare_commits": self.compare_commits,
            "create_branch": self.create_branch,
            "delete_branch": self.delete_branch,
            "list_branches": self.list_branches,
            "get_branch": self.get_branch,
            "add_collaborator": self.add_collaborator,
            "remove_collaborator": self.remove_collaborator,
            "list_collaborators": self.list_collaborators,
            "check_collaborator": self.check_collaborator,
            "create_milestone": self.create_milestone,
            "close_milestone": self.close_milestone,
            "update_milestone": self.update_milestone,
            "list_milestones": self.list_milestones,
            "get_milestone": self.get_milestone,
            "create_label": self.create_label,
            "delete_label": self.delete_label,
            "update_label": self.update_label,
            "list_labels": self.list_labels,
            "get_label": self.get_label,
            "create_webhook": self.create_webhook,
            "delete_webhook": self.delete_webhook,
            "list_webhooks": self.list_webhooks,
            "get_webhook": self.get_webhook,
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

    # Commit Management Methods
    def create_commit(
        self,
        repo_name: str,
        path: str,
        message: str,
        content: str,
        branch: str = "main",
    ) -> str:
        try:
            repo = self._github.get_repo(repo_name)
            repo.create_file(path=path, message=message, content=content, branch=branch)
            return f"Commit created successfully at {path}."
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
