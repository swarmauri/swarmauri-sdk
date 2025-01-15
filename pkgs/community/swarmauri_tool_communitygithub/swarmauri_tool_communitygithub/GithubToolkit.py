# File: swarmauri/standard/toolkits/concrete/GithubToolkit.py
from typing import Literal, Optional

from pydantic import BaseModel

from swarmauri_base.toolkits.ToolkitBase import ToolkitBase
from swarmauri_tool_communitygithub.GithubRepoTool import GithubRepoTool
from swarmauri_tool_communitygithub.GithubIssueTool import GithubIssueTool
from swarmauri_tool_communitygithub.GithubPRTool import GithubPRTool
from swarmauri_tool_communitygithub.GithubBranchTool import GithubBranchTool
from swarmauri_tool_communitygithub.GithubCommitTool import GithubCommitTool

from dotenv import load_dotenv

load_dotenv()


class GithubToolkit(ToolkitBase):
    type: Literal["GithubToolkit"] = "GithubToolkit"
    resource: str = "GithubToolkit"

    token: str = None
    # Explicitly define the tools as fields
    github_repo_tool: Optional[GithubRepoTool] = None
    github_issue_tool: Optional[GithubIssueTool] = None
    github_pr_tool: Optional[GithubPRTool] = None
    github_branch_tool: Optional[GithubBranchTool] = None
    github_commit_tool: Optional[GithubCommitTool] = None

    def __init__(self, token: str, **kwargs):
        super().__init__(**kwargs)

        if not token:
            raise ValueError("Invalid Token or Missing token")

        self.token = token

        self.github_repo_tool = GithubRepoTool(token=self.token)
        self.github_issue_tool = GithubIssueTool(token=self.token)
        self.github_pr_tool = GithubPRTool(token=self.token)
        self.github_branch_tool = GithubBranchTool(token=self.token)
        self.github_commit_tool = GithubCommitTool(token=self.token)

        self.add_tool(self.github_repo_tool)
        self.add_tool(self.github_issue_tool)
        self.add_tool(self.github_pr_tool)
        self.add_tool(self.github_commit_tool)
        self.add_tool(self.github_branch_tool)

    # @model_validator(mode="wrap")
    # @classmethod
    # def validate_model(cls, values: Any, handler: Any):
    #     # Extract the tools and validate their types manually
    #     tools = values.get("tools", {})

    #     for tool_name, tool_data in tools.items():
    #         if isinstance(tool_data, dict):
    #             tool_type = tool_data.get("type")
    #             tool_id = tool_data.get("id")  # Preserve the ID if it exists

    #             try:
    #                 tool_class = next(
    #                     sub_cls
    #                     for sub_cls in SubclassUnion.__swm__get_subclasses__(ToolBase)
    #                     if sub_cls.__name__ == tool_type
    #                 )

    #                 # # Create an instance of the tool class
    #                 tools[tool_name] = tool_class(**tool_data)
    #                 tools[tool_name].id = (
    #                     tool_id  # Ensure the tool ID is not changed unintentionally
    #                 )
    #             except StopIteration:
    #                 raise ValueError(f"Unknown tool type: {tool_type}")

    #     values["tools"] = tools
    #     return handler(values)
