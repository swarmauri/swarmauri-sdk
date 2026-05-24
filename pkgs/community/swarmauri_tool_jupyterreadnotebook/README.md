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

# Swarmauri Jupyter Read Notebook Tool

`swarmauri_tool_jupyterreadnotebook` reads a Jupyter `.ipynb` file from disk, parses it with `nbformat`, validates the notebook schema, and returns the resulting `NotebookNode` inside a Swarmauri tool response.

## Why

- Load notebooks into Swarmauri pipelines before execution, export, or cleanup steps.
- Normalize notebook ingestion around a simple tool contract.
- Catch missing files and notebook schema issues before later notebook-processing stages.

## Features

- Reads `.ipynb` files with `nbformat.read`.
- Validates the parsed notebook with `nbformat.validate`.
- Returns `{"notebook_node": ...}` on success.
- Returns `{"error": ...}` on file and validation failures.
- Supports an `as_version` argument for controlled notebook parsing.

## FAQ

### What does this tool return?

It returns a dictionary with either `notebook_node` containing the parsed notebook or `error` containing a failure message.

### Does this tool execute the notebook?

No. It only reads and validates notebook content. Pair it with execution tools when you need code-cell outputs.

### When should I change `as_version`?

Use `as_version` when you need to coerce notebook parsing to a specific `nbformat` version for compatibility with downstream tooling.

## Installation

```bash
uv add swarmauri_tool_jupyterreadnotebook
```

```bash
pip install swarmauri_tool_jupyterreadnotebook
```

## Usage

```python
from swarmauri_tool_jupyterreadnotebook import JupyterReadNotebookTool

tool = JupyterReadNotebookTool()
result = tool(
    notebook_file_path="notebooks/example.ipynb",
    as_version=4,
)

if "notebook_node" in result:
    notebook = result["notebook_node"]
    print(len(notebook.cells))
else:
    print(result["error"])
```

## Examples

### Read a notebook before execution

```python
from swarmauri_tool_jupyterreadnotebook import JupyterReadNotebookTool

reader = JupyterReadNotebookTool()
payload = reader("reports/daily_report.ipynb")

if "notebook_node" in payload:
    metadata = payload["notebook_node"].metadata
    print(metadata)
```

### Guard against invalid notebook files

```python
response = JupyterReadNotebookTool()("broken.ipynb")

if "error" in response:
    print("Notebook ingestion failed:", response["error"])
```

## Related Packages

- [`swarmauri_tool_jupyterwritenotebook`](https://pypi.org/project/swarmauri_tool_jupyterwritenotebook/)
- [`swarmauri_tool_jupyterexecutenotebook`](https://pypi.org/project/swarmauri_tool_jupyterexecutenotebook/)
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
- [nbformat documentation](https://nbformat.readthedocs.io/)
- [Jupyter notebook format docs](https://jupyter.org/documentation)
