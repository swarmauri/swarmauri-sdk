![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_toolkit_github/">
        <img src="https://static.pepy.tech/badge/swarmauri_toolkit_github/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_toolkit_github/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_toolkit_github.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_github/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_github/">
        <img src="https://img.shields.io/pypi/l/swarmauri_toolkit_github" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_github/">
        <img src="https://img.shields.io/pypi/v/swarmauri_toolkit_github?label=swarmauri_toolkit_github&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri Toolkit GitHub

Github Toolkit.

## Features

- Github Toolkit.
- Exposes discoverable runtime entry points for `swarmauri.toolkits, swarmauri.tools` so the package can be wired into Swarmauri or Tigrbl workflows.
- Lives in the community package lane for optional integrations that extend the main Swarmauri SDK surface.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_toolkit_github
```

```bash
pip install swarmauri_toolkit_github
```

## Usage

Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it.

```python
from swarmauri_toolkit_github import GithubBranchTool, GithubCommitTool, GithubIssueTool, GithubPRTool

exports = ['GithubBranchTool', 'GithubCommitTool', 'GithubIssueTool', 'GithubPRTool']
print(exports)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
