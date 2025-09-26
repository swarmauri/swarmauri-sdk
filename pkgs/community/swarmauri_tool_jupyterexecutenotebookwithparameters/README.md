![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutenotebookwithparameters/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterexecutenotebookwithparameters" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecutenotebookwithparameters/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecutenotebookwithparameters.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutenotebookwithparameters/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterexecutenotebookwithparameters" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutenotebookwithparameters/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterexecutenotebookwithparameters" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutenotebookwithparameters/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexecutenotebookwithparameters?label=swarmauri_tool_jupyterexecutenotebookwithparameters&color=green" alt="PyPI - swarmauri_tool_jupyterexecutenotebookwithparameters"/></a>
</p>

---

# Swarmauri Tool Jupyter Execute Notebook With Parameters

Runs a Jupyter notebook with injected parameters using Papermill-style execution.

## Features

- Parameterizes notebooks via Papermill and executes them end-to-end.
- Saves the executed notebook to an output path of your choice.
- Returns a dict containing `executed_notebook` on success or `error`/`message` when execution fails.

## Prerequisites

- Python 3.10 or newer.
- Papermill, nbformat, nbconvert, swarmauri base/core packages (installed automatically).
- Notebook dependencies must be available in the runtime environment.

## Installation

```bash
# pip
pip install swarmauri_tool_jupyterexecutenotebookwithparameters

# poetry
poetry add swarmauri_tool_jupyterexecutenotebookwithparameters

# uv (pyproject-based projects)
uv add swarmauri_tool_jupyterexecutenotebookwithparameters
```

## Quickstart

```python
from swarmauri_tool_jupyterexecutenotebookwithparameters import JupyterExecuteNotebookWithParametersTool

executor = JupyterExecuteNotebookWithParametersTool()
response = executor(
    notebook_path="templates/report.ipynb",
    output_notebook_path="outputs/report-filled.ipynb",
    params={
        "input_data_path": "data/input.csv",
        "run_mode": "production",
    },
    timeout=600,
)

if "executed_notebook" in response:
    print("Notebook executed:", response["executed_notebook"])
else:
    print("Error:", response["error"], response.get("message"))
```

## Tips

- Parameters can be any JSON-serializable values used inside the notebook (strings, numbers, dictionaries, etc.).
- Increase `timeout` for notebooks with lengthy cells.
- Combine with Swarmauri notebook cleaning/conversion tools for full pipelines (execute → clear outputs → convert to PDF/HTML).

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
