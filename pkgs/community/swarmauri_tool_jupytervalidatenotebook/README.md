![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_jupytervalidatenotebook/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_jupytervalidatenotebook/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupytervalidatenotebook/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupytervalidatenotebook.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupytervalidatenotebook/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupytervalidatenotebook/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupytervalidatenotebook" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupytervalidatenotebook/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupytervalidatenotebook?label=swarmauri_tool_jupytervalidatenotebook&color=green" alt="PyPI - swarmauri_tool_jupytervalidatenotebook"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Jupyter Validate Notebook Tool

`swarmauri_tool_jupytervalidatenotebook` validates a notebook object against Jupyter notebook schema rules with `nbformat` and returns a structured validity report for Swarmauri notebook workflows.

## Why

- Catch notebook structure problems before execution or export.
- Add a simple schema-validation gate to notebook automation pipelines.
- Standardize notebook health checks behind a Swarmauri tool contract.

## Features

- Accepts notebook objects compatible with `nbformat`.
- Enforces `nbformat == 4` before schema validation.
- Validates notebook structure with `nbformat.validate`.
- Returns `valid` and `report` fields for downstream flow control.
- Handles validation and unexpected runtime failures explicitly.

## FAQ

### What does this tool return?

It returns a dictionary with `valid` set to `"True"` or `"False"` and a human-readable `report` describing the outcome.

### Does this tool accept notebook file paths?

No. It expects a notebook object, not a path and not a JSON string.

### Why does it reject notebooks with the wrong `nbformat`?

The implementation explicitly requires Jupyter notebook format version 4 before calling schema validation.

## Installation

```bash
uv add swarmauri_tool_jupytervalidatenotebook
```

```bash
pip install swarmauri_tool_jupytervalidatenotebook
```

## Usage

```python
from swarmauri_tool_jupytervalidatenotebook import JupyterValidateNotebookTool

notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "cells": [],
    "metadata": {},
}

result = JupyterValidateNotebookTool()(notebook=notebook)
print(result)
```

## Examples

### Validate a notebook before execution

```python
validator = JupyterValidateNotebookTool()
result = validator(
    notebook={
        "nbformat": 4,
        "nbformat_minor": 5,
        "cells": [],
        "metadata": {},
    }
)

if result["valid"] == "True":
    print("Notebook passed validation")
```

### Detect invalid notebook version

```python
result = JupyterValidateNotebookTool()(
    notebook={
        "nbformat": 3,
        "nbformat_minor": 0,
        "cells": [],
        "metadata": {},
    }
)

print(result["report"])
```

## Related Packages

- [`swarmauri_tool_jupyterfromdict`](https://pypi.org/project/swarmauri_tool_jupyterfromdict/)
- [`swarmauri_tool_jupyterreadnotebook`](https://pypi.org/project/swarmauri_tool_jupyterreadnotebook/)
- [`swarmauri_tool_jupyterwritenotebook`](https://pypi.org/project/swarmauri_tool_jupyterwritenotebook/)
- [`swarmauri_tool_jupyterexecutenotebook`](https://pypi.org/project/swarmauri_tool_jupyterexecutenotebook/)
- [`swarmauri_tool_jupyterclearoutput`](https://pypi.org/project/swarmauri_tool_jupyterclearoutput/)

## Foundational Swarmauri Packages

- [`swarmauri`](https://pypi.org/project/swarmauri/)
- [`swarmauri_core`](https://pypi.org/project/swarmauri_core/)
- [`swarmauri_base`](https://pypi.org/project/swarmauri_base/)
- [`swarmauri_standard`](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)
- [nbformat documentation](https://nbformat.readthedocs.io/)
- [Jupyter documentation](https://jupyter.org/documentation)
