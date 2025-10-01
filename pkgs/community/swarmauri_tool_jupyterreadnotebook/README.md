![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterreadnotebook/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterreadnotebook" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterreadnotebook/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterreadnotebook.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterreadnotebook/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterreadnotebook" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterreadnotebook/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterreadnotebook" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterreadnotebook/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterreadnotebook?label=swarmauri_tool_jupyterreadnotebook&color=green" alt="PyPI - swarmauri_tool_jupyterreadnotebook"/></a>
</p>

---

# Swarmauri Tool Jupyter Read Notebook

Reads a `.ipynb` file from disk into a validated nbformat `NotebookNode` for downstream processing.

## Features

- Wraps nbformat’s `read` + validation workflow in a Swarmauri tool.
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

- Use with execution/export tools to build pipelines (read → execute → convert).
- Handle `error` key gracefully when files are missing or malformed.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
