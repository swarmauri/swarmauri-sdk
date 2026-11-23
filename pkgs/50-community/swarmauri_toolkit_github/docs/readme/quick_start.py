import os
from swarmauri_toolkit_github import GithubToolkit

toolkit = GithubToolkit(api_token=os.environ["GITHUB_TOKEN"])

# List repositories for the authenticated user
repos = toolkit.github_repo_tool(action="list_repos")
print(repos["list_repos"])

# Open a tracking issue
issue = toolkit.github_issue_tool(
    action="create_issue",
    repo_name="owner/example",
    title="Investigate flaky tests",
    body="Logs: https://gist.github.com/...",
)
print(issue["create_issue"])
