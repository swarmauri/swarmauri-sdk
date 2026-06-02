![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_jupyterexecutenotebookwithparameters/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_jupyterexecutenotebookwithparameters/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecutenotebookwithparameters/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecutenotebookwithparameters.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutenotebookwithparameters/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutenotebookwithparameters/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterexecutenotebookwithparameters" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutenotebookwithparameters/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexecutenotebookwithparameters?label=swarmauri_tool_jupyterexecutenotebookwithparameters&color=green" alt="PyPI - swarmauri_tool_jupyterexecutenotebookwithparameters"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Jupyter Execute Notebook With Parameters Tool

`swarmauri_tool_jupyterexecutenotebookwithparameters` executes parameterized Jupyter notebooks through `papermill`, injects runtime parameters, and writes the executed notebook to a target output path.

## Why

- Turn notebooks into repeatable jobs with runtime inputs.
- Generate environment-specific notebook runs without hand-editing source notebooks.
- Use papermill-backed parameter injection inside Swarmauri workflows.

## Features

- Executes `.ipynb` notebooks with `papermill.execute_notebook`.
- Injects a dictionary of runtime parameters.
- Writes results to a caller-provided output notebook path.
- Validates that both input and output paths are notebook files.
- Returns either `{"executed_notebook": ...}` or `{"error": ...}`.

## FAQ

### When should I use this package instead of `swarmauri_tool_jupyterexecutenotebook`?

Use this package when the notebook needs injected parameters and a persisted executed output file. Use `swarmauri_tool_jupyterexecutenotebook` for direct in-memory execution and a returned `NotebookNode`.

### Does this tool require `.ipynb` paths?

Yes. Both `notebook_path` and `output_notebook_path` must end with `.ipynb`, or the tool returns an error.

### What does the parameter payload look like?

It is a plain Python dictionary that papermill passes into the notebook parameter cell.

## Installation

```bash
uv add swarmauri_tool_jupyterexecutenotebookwithparameters
```

```bash
pip install swarmauri_tool_jupyterexecutenotebookwithparameters
```

## Usage

```python
from swarmauri_tool_jupyterexecutenotebookwithparameters import (
    JupyterExecuteNotebookWithParametersTool,
)

tool = JupyterExecuteNotebookWithParametersTool()
result = tool(
    notebook_path="templates/report.ipynb",
    output_notebook_path="artifacts/report-executed.ipynb",
    params={"region": "us", "day": "2026-05-24"},
)

print(result)
```

## Examples

### Execute a report notebook for a specific tenant

```python
tool = JupyterExecuteNotebookWithParametersTool()

response = tool(
    notebook_path="reports/monthly.ipynb",
    output_notebook_path="artifacts/monthly-acme.ipynb",
    params={"tenant_id": "acme", "month": "2026-05"},
)

print(response["executed_notebook"])
```

### Handle invalid notebook extensions

```python
response = JupyterExecuteNotebookWithParametersTool()(
    notebook_path="reports/monthly.txt",
    output_notebook_path="artifacts/monthly.ipynb",
)

if "error" in response:
    print(response["error"])
```

## Related Packages

- [`swarmauri_tool_jupyterexecutenotebook`](https://pypi.org/project/swarmauri_tool_jupyterexecutenotebook/)
- [`swarmauri_tool_jupyterreadnotebook`](https://pypi.org/project/swarmauri_tool_jupyterreadnotebook/)
- [`swarmauri_tool_jupyterwritenotebook`](https://pypi.org/project/swarmauri_tool_jupyterwritenotebook/)
- [`swarmauri_tool_jupyterexecuteandconvert`](https://pypi.org/project/swarmauri_tool_jupyterexecuteandconvert/)
- [`swarmauri_tool_jupyterclearoutput`](https://pypi.org/project/swarmauri_tool_jupyterclearoutput/)

## Foundational Swarmauri Packages

- [`swarmauri`](https://pypi.org/project/swarmauri/)
- [`swarmauri_core`](https://pypi.org/project/swarmauri_core/)
- [`swarmauri_base`](https://pypi.org/project/swarmauri_base/)
- [`swarmauri_standard`](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)
- [Papermill documentation](https://papermill.readthedocs.io/)
- [Jupyter notebook documentation](https://jupyter.org/documentation)
