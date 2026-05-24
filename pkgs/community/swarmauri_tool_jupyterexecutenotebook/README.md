![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_jupyterexecutenotebook/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_jupyterexecutenotebook/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecutenotebook/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecutenotebook.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutenotebook/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutenotebook/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterexecutenotebook" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutenotebook/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexecutenotebook?label=swarmauri_tool_jupyterexecutenotebook&color=green" alt="PyPI - swarmauri_tool_jupyterexecutenotebook"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool Jupyter Execute Notebook

Executes all cells of a Jupyter notebook using nbclient and returns the executed `NotebookNode` with captured outputs.

## Features

- Runs notebooks programmatically via the Swarmauri tool interface.
- Accepts optional per-cell timeout (default 30 seconds) and continues on cell errors.
- Returns the executed notebook object so downstream tools can inspect outputs or save it.

## Prerequisites

- Python 3.10 or newer.
- Jupyter/nbconvert stack available (`nbclient`, `nbformat`, `ipykernel`, etc.â€”installed automatically).
- Notebook dependencies must be installed in the environment where the tool runs.

## Installation

```bash
# pip
pip install swarmauri_tool_jupyterexecutenotebook

# poetry
poetry add swarmauri_tool_jupyterexecutenotebook

# uv (pyproject-based projects)
uv add swarmauri_tool_jupyterexecutenotebook
```

## Quickstart

```python
from swarmauri_tool_jupyterexecutenotebook import JupyterExecuteNotebookTool

executor = JupyterExecuteNotebookTool()
executed_nb = executor(
    notebook_path="notebooks/example.ipynb",
    timeout=120,
)

# Save the executed notebook
import nbformat, json
from pathlib import Path

Path("notebooks/example-executed.ipynb").write_text(
    nbformat.writes(executed_nb),
    encoding="utf-8",
)
```

## Tips

- Increase `timeout` for notebooks with long-running cells to avoid `CellTimeoutError`.
- Set `allow_errors=True` (default in the tool) so execution continues after a failing cell while error traces are still recorded.
- Combine with `JupyterClearOutputTool` or conversion tools to build end-to-end notebook pipelines.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.


