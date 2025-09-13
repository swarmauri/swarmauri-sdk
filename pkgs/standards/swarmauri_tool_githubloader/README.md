<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_githubloader/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_githubloader" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_githubloader/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_githubloader.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_githubloader/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_githubloader" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_githubloader/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_githubloader" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_githubloader/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_githubloader?label=swarmauri_tool_githubloader&color=green" alt="PyPI - swarmauri_tool_githubloader"/></a>
</p>

---

# Swarmauri Tool GithubLoader

Load YAML-defined components directly from GitHub repositories.

## Installation

```bash
pip install swarmauri_tool_githubloader
```

## Usage

```python
from swarmauri_tool_githubloader import GithubLoadedTool

# Load a tool from GitHub
tool = GithubLoadedTool(
    owner="myorg",
    repo="myrepo",
    path="tools/addition.yaml",
)

# Use like any other tool
result = tool(x=1, y=2)
```

### Options

Customize how the loader fetches your component:

- **branch** – Branch to read from (defaults to `"main"`).
- **commit_ref** – Specific commit SHA; overrides `branch` when provided.
- **token** – GitHub token for private repositories.
- **use_cache** – Set to `False` to reload the component on every call.

### Advanced examples

Fetch from a branch and pin a commit:

```python
tool = GithubLoadedTool(
    owner="myorg",
    repo="myrepo",
    path="tools/addition.yaml",
    branch="develop",
    commit_ref="0123456789abcdef",
)
```

Load from a private repository with caching disabled:

```python
import os

tool = GithubLoadedTool(
    owner="myorg",
    repo="private-repo",
    path="tools/addition.yaml",
    token=os.environ["GITHUB_TOKEN"],
    use_cache=False,
)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
