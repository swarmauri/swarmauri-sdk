
![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_toolkit_github/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_toolkit_github" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_toolkit_github/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_toolkit_github.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_github/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_toolkit_github" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_github/">
        <img src="https://img.shields.io/pypi/l/swarmauri_toolkit_github" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_github/">
        <img src="https://img.shields.io/pypi/v/swarmauri_toolkit_github?label=swarmauri_toolkit_github&color=green" alt="PyPI - swarmauri_toolkit_github"/></a>
</p>

---

# Swarmauri Toolkit Github

A collection of GitHub tools for repository, issue, pull request, branch, and commit management using PyGithub.

## Features
- Unified interface for core GitHub automation tasks (repositories, branches, commits, issues, and pull requests).
- Token-aware helper that authenticates once and shares the session across every tool call.
- Friendly responses containing both status metadata and the PyGithub payload, ready for downstream automation.
- Extensible action vocabulary that mirrors PyGithub so you can grow beyond the examples below.

## Prerequisites
- Python 3.10 or newer.
- A GitHub personal access token with the scopes your workflow needs. Store it securely, e.g. `export GITHUB_TOKEN="ghp_..."`.

## Installation

```bash
# pip
pip install swarmauri_toolkit_github

# poetry
poetry add swarmauri_toolkit_github

# uv (pyproject-based projects)
uv add swarmauri_toolkit_github
```

## Quickstart

Authenticate once and reuse the toolkit across different GitHub resources:

```python
from swarmauri.toolkits.GithubToolkit import GithubToolkit

toolkit = GithubToolkit(token="your_github_token")

# Create a repository
repo_result = toolkit.github_repo_tool(
    action="create_repo",
    repo_name="my-new-repo"
)
print(repo_result["status"], repo_result["payload"].html_url)

# File an issue
issue_result = toolkit.github_issue_tool(
    action="create_issue",
    repo_name="owner/repository",
    title="Bug Report",
    body="Description of the issue"
)
print(f"Opened issue #{issue_result['payload'].number}")

# Open a pull request
pr_result = toolkit.github_pr_tool(
    action="create_pull",
    repo_name="owner/repository",
    title="New Feature",
    head="feature-branch",
    base="main"
)
print(f"Opened PR #{pr_result['payload'].number}")
```

## Advanced Usage

Read-only and follow-up actions use the same tools by switching the `action` argument:

```python
from swarmauri.toolkits.GithubToolkit import GithubToolkit

toolkit = GithubToolkit(token="your_github_token")

# Inspect repository metadata
repo_info = toolkit.github_repo_tool(
    action="get_repo",
    repo_name="owner/repository"
)
print(repo_info["payload"].full_name, repo_info["payload"].stargazers_count)

# List open pull requests
prs = toolkit.github_pr_tool(
    action="list",
    repo_name="owner/repository",
    state="open"
)
for pr in prs["payload"]:
    print(f"#{pr.number} {pr.title} by {pr.user.login}")

# Leave a triage comment on an issue
toolkit.github_issue_tool(
    action="create_comment",
    repo_name="owner/repository",
    number=123,
    body="Thanks for the report! We're looking into it."
)
```

### Best Practices
- Inject your token via environment variables or your secrets manager rather than hard-coding it.
- Combine this toolkit with other Swarmauri agents for end-to-end automation (e.g. triaging issues to PR creation).
- Handle rate limiting by catching PyGithub exceptions and retrying with exponential backoff.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
