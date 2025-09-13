
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

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

