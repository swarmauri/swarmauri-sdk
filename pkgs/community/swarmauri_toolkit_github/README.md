
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_toolkit_github/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_toolkit_github" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_toolkit_github/README.md">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_toolkit_github/README.md&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
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

## Installation

```bash
pip install swarmauri_toolkit_github
```

## Usage

Here's a basic example using the GitHub toolkit:

```python
from swarmauri.toolkits.GithubToolkit import GithubToolkit

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

