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

# Swarmauri Jupyter Execute Notebook Tool

`swarmauri_tool_jupyterexecutenotebook` executes every cell in a Jupyter notebook with `nbclient`, captures notebook outputs in-place, and returns the executed `NotebookNode` for downstream processing.

## Why

- Run notebooks inside Swarmauri workflows without shelling out to a separate notebook runner.
- Capture generated outputs for reporting, validation, or export steps.
- Keep notebook execution inside a simple Python tool contract.

## Features

- Loads notebooks from disk with `nbformat`.
- Executes all cells with `nbclient.NotebookClient`.
- Returns the executed notebook object rather than a file path.
- Supports per-cell execution timeout control.
- Uses `allow_errors=True`, so the notebook can retain partial outputs even when a cell fails.

## FAQ

### What does this tool return?

It returns the `NotebookNode` after execution. If execution fails partway through, the tool still returns the notebook object so callers can inspect partial output.

### Does it stop on the first cell error?

No. The underlying client is created with `allow_errors=True`, which preserves notebook state and outputs even when cells fail.

### When should I use this instead of the parameterized execution tool?

Use this package for direct notebook execution. Use `swarmauri_tool_jupyterexecutenotebookwithparameters` when you need papermill-style parameter injection and an output notebook path.

## Installation

```bash
uv add swarmauri_tool_jupyterexecutenotebook
```

```bash
pip install swarmauri_tool_jupyterexecutenotebook
```

## Usage

```python
from swarmauri_tool_jupyterexecutenotebook import JupyterExecuteNotebookTool

tool = JupyterExecuteNotebookTool()
executed = tool("notebooks/report.ipynb", timeout=60)

for cell in executed.cells:
    if cell.get("outputs"):
        print(cell["outputs"])
```

## Examples

### Execute a notebook before export

```python
from swarmauri_tool_jupyterexecutenotebook import JupyterExecuteNotebookTool

tool = JupyterExecuteNotebookTool()
notebook = tool("analytics/daily_metrics.ipynb", timeout=120)

print(len(notebook.cells))
```

### Inspect partial output after a failing cell

```python
executed = JupyterExecuteNotebookTool()("debug/failing_notebook.ipynb")

for index, cell in enumerate(executed.cells):
    print(index, cell.get("outputs", []))
```

## Related Packages

- [`swarmauri_tool_jupyterreadnotebook`](https://pypi.org/project/swarmauri_tool_jupyterreadnotebook/)
- [`swarmauri_tool_jupyterwritenotebook`](https://pypi.org/project/swarmauri_tool_jupyterwritenotebook/)
- [`swarmauri_tool_jupyterexecutenotebookwithparameters`](https://pypi.org/project/swarmauri_tool_jupyterexecutenotebookwithparameters/)
- [`swarmauri_tool_jupyterexecuteandconvert`](https://pypi.org/project/swarmauri_tool_jupyterexecuteandconvert/)
- [`swarmauri_tool_jupyterclearoutput`](https://pypi.org/project/swarmauri_tool_jupyterclearoutput/)

## Foundational Swarmauri Packages

- [`swarmauri`](https://pypi.org/project/swarmauri/)
- [`swarmauri_core`](https://pypi.org/project/swarmauri_core/)
- [`swarmauri_base`](https://pypi.org/project/swarmauri_base/)
- [`swarmauri_standard`](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)
- [nbclient documentation](https://nbclient.readthedocs.io/)
- [nbformat documentation](https://nbformat.readthedocs.io/)
