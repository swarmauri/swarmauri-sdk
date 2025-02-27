from typing import Literal, Optional

from dotenv import load_dotenv
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase

from swarmauri_toolkit_github.GithubBranchTool import GithubBranchTool
from swarmauri_toolkit_github.GithubCommitTool import GithubCommitTool
from swarmauri_toolkit_github.GithubIssueTool import GithubIssueTool
from swarmauri_toolkit_github.GithubPRTool import GithubPRTool
from swarmauri_toolkit_github.GithubRepoTool import GithubRepoTool

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
            raise ValueError("Invalid Token or Missing api_token")

        self.api_token = api_token

        self.github_repo_tool = GithubRepoTool(api_token=self.api_token)
        self.github_issue_tool = GithubIssueTool(api_token=self.api_token)
        self.github_pr_tool = GithubPRTool(api_token=self.api_token)
        self.github_branch_tool = GithubBranchTool(api_token=self.api_token)
        self.github_commit_tool = GithubCommitTool(api_token=self.api_token)

        self.add_tool(self.github_repo_tool)
        self.add_tool(self.github_issue_tool)
        self.add_tool(self.github_pr_tool)
        self.add_tool(self.github_commit_tool)
        self.add_tool(self.github_branch_tool)
