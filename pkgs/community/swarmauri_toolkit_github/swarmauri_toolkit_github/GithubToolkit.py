from typing import Literal, Optional

from swarmauri_core.ComponentBase import ComponentBase

from swarmauri_base.toolkits.ToolkitBase import ToolkitBase
from swarmauri_toolkit_github.GithubRepoTool import GithubRepoTool
from swarmauri_toolkit_github.GithubIssueTool import GithubIssueTool
from swarmauri_toolkit_github.GithubPRTool import GithubPRTool
from swarmauri_toolkit_github.GithubBranchTool import GithubBranchTool
from swarmauri_toolkit_github.GithubCommitTool import GithubCommitTool

from dotenv import load_dotenv

load_dotenv()


@ComponentBase.register_type(ToolkitBase, "GithubToolkit")
class GithubToolkit(ToolkitBase):
    type: Literal["GithubToolkit"] = "GithubToolkit"
    api_token: str = None
    # Explicitly define the tools as fields
    github_repo_tool: Optional[GithubRepoTool] = None
    github_issue_tool: Optional[GithubIssueTool] = None
    github_pr_tool: Optional[GithubPRTool] = None
    github_branch_tool: Optional[GithubBranchTool] = None
    github_commit_tool: Optional[GithubCommitTool] = None

    def __init__(self, api_token: str, **kwargs):
        super().__init__(**kwargs)

        if not api_token:
            raise ValueError("Invalid Token or Missing token")

        self.api_token = api_token

        self.github_repo_tool = GithubRepoTool(token=self.api_token)
        self.github_issue_tool = GithubIssueTool(token=self.api_token)
        self.github_pr_tool = GithubPRTool(token=self.token)
        self.github_branch_tool = GithubBranchTool(token=self.api_token)
        self.github_commit_tool = GithubCommitTool(token=self.api_token)

        self.add_tool(self.github_repo_tool)
        self.add_tool(self.github_issue_tool)
        self.add_tool(self.github_pr_tool)
        self.add_tool(self.github_commit_tool)
        self.add_tool(self.github_branch_tool)
