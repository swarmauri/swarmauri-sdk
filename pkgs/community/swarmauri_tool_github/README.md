![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_github)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri-tool-github)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_tool_github)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri-tool-github?label=swarmauri_tool_github&color=green)

</div>

---

# GitHub Tools Package

A collection of GitHub tools for repository, issue, pull request, branch, and commit management using PyGithub.

## Installation

```bash
pip install swarmauri_tool_github
```

## Usage

Here's a basic example using the GitHub toolkit:

```python
from swarmauri.tools.GithubToolkit import GithubToolkit

# Initialize the toolkit with your GitHub token
toolkit = GithubToolkit(token="your_github_token")

# Create a repository
result = toolkit.github_repo_tool(
    action="create_repo",
    repo_name="my-new-repo"
)

# Create an issue
result = toolkit.github_issue_tool(
    action="create_issue",
    repo_name="owner/repository",
    title="Bug Report",
    body="Description of the issue"
)

# Create a pull request
result = toolkit.github_pr_tool(
    action="create_pull",
    repo_name="owner/repository",
    title="New Feature",
    head="feature-branch",
    base="main"
)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

