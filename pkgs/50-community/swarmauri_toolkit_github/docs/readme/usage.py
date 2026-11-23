import os
from swarmauri_toolkit_github import GithubToolkit

toolkit = GithubToolkit(api_token=os.environ["GITHUB_TOKEN"])

# Create a release branch
toolkit.github_branch_tool(
    action="create_branch",
    repo_name="owner/service",
    new_branch="release/v1.4.0",
    source_branch="master",
)

# Cut a changelog commit
toolkit.github_commit_tool(
    action="create_file",
    repo_name="owner/service",
    path="CHANGELOG.md",
    message="Add release notes",
    content="### v1.4.0\n- New features...",
    branch="release/v1.4.0",
)
