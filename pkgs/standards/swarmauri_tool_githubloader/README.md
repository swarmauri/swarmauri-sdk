![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

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

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
