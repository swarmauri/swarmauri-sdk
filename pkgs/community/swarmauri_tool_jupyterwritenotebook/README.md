![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_jupyterwritenotebook/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_jupyterwritenotebook/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterwritenotebook/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterwritenotebook.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterwritenotebook/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterwritenotebook/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterwritenotebook" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterwritenotebook/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterwritenotebook?label=swarmauri_tool_jupyterwritenotebook&color=green" alt="PyPI - swarmauri_tool_jupyterwritenotebook"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Jupyter Write Notebook Tool

`swarmauri_tool_jupyterwritenotebook` writes notebook data to disk as JSON, then reads the file back to confirm the notebook artifact is not empty. It is useful when Swarmauri workflows materialize generated or transformed notebooks.

## Why

- Persist notebook data generated in memory by other notebook tools.
- Save cleaned, parameterized, or post-processed notebook artifacts to versioned paths.
- Add a simple write-and-verify step to notebook automation pipelines.

## Features

- Accepts notebook content as a dictionary or `NotebookNode`-compatible structure.
- Writes `.ipynb` JSON with configurable text encoding.
- Performs a read-back verification step after the write.
- Returns a success payload with the output file path.
- Returns `{"error": ...}` when writing or verification fails.

## FAQ

### Does this tool validate notebook schema?

No. It writes the provided structure as JSON and verifies that the file can be read back. Pair it with notebook-read or notebook-validation steps if you need strict schema checks.

### What happens if the notebook payload is empty?

The tool writes the file, then fails verification and returns an error because the round-tripped content is empty.

### Can I choose the output encoding?

Yes. The `encoding` parameter defaults to `utf-8`, but you can override it when needed.

## Installation

```bash
uv add swarmauri_tool_jupyterwritenotebook
```

```bash
pip install swarmauri_tool_jupyterwritenotebook
```

## Usage

```python
from swarmauri_tool_jupyterwritenotebook import JupyterWriteNotebookTool

tool = JupyterWriteNotebookTool()
result = tool(
    notebook_data={
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {},
        "cells": [],
    },
    output_file="artifacts/output.ipynb",
)

print(result)
```

## Examples

### Save a transformed notebook

```python
from swarmauri_tool_jupyterwritenotebook import JupyterWriteNotebookTool

notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {},
    "cells": [
        {"cell_type": "markdown", "metadata": {}, "source": ["# Report"]},
    ],
}

response = JupyterWriteNotebookTool()(
    notebook_data=notebook,
    output_file="reports/report.ipynb",
)

print(response["file_path"])
```

### Handle write failures

```python
response = JupyterWriteNotebookTool()(
    notebook_data={},
    output_file="reports/empty.ipynb",
)

if "error" in response:
    print(response["error"])
```

## Related Packages

- [`swarmauri_tool_jupyterreadnotebook`](https://pypi.org/project/swarmauri_tool_jupyterreadnotebook/)
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
