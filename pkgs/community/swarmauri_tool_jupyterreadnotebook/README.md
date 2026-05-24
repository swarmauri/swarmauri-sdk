![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_jupyterreadnotebook/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_jupyterreadnotebook/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterreadnotebook/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterreadnotebook.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterreadnotebook/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterreadnotebook/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterreadnotebook" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterreadnotebook/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterreadnotebook?label=swarmauri_tool_jupyterreadnotebook&color=green" alt="PyPI - swarmauri_tool_jupyterreadnotebook"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool Jupyter Read Notebook

Reads a `.ipynb` file from disk into a validated nbformat `NotebookNode` for downstream processing.

## Features

- Wraps nbformatâ€™s `read` + validation workflow in a Swarmauri tool.
- Returns `{ "notebook_node": NotebookNode }` on success or `{ "error": ... }` on failure.
- Optional `as_version` argument controls notebook parsing version (default 4).

## Prerequisites

- Python 3.10 or newer.
- nbformat installed (pulled automatically).

## Installation

```bash
# pip
pip install swarmauri_tool_jupyterreadnotebook

# poetry
poetry add swarmauri_tool_jupyterreadnotebook

# uv (pyproject-based projects)
uv add swarmauri_tool_jupyterreadnotebook
```

## Quickstart

```python
from swarmauri_tool_jupyterreadnotebook import JupyterReadNotebookTool

reader = JupyterReadNotebookTool()
response = reader(
    notebook_file_path="notebooks/example.ipynb",
    as_version=4,
)

if "notebook_node" in response:
    nb = response["notebook_node"]
    print("Cells:", len(nb.cells))
else:
    print("Error:", response["error"])
```

## Tips

- Use with execution/export tools to build pipelines (read â†’ execute â†’ convert).
- Handle `error` key gracefully when files are missing or malformed.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.


