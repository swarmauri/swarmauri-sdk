![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_jupyterfromdict/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_jupyterfromdict/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterfromdict/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterfromdict.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterfromdict/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterfromdict/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterfromdict" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterfromdict/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterfromdict?label=swarmauri_tool_jupyterfromdict&color=green" alt="PyPI - swarmauri_tool_jupyterfromdict"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Jupyter From Dict Tool

`swarmauri_tool_jupyterfromdict` converts a plain Python dictionary into a validated `NotebookNode` with `nbformat`, making it useful for programmatic notebook construction inside Swarmauri workflows.

## Why

- Build notebook objects from generated or transformed Python data.
- Normalize notebook creation behind a simple tool contract.
- Validate notebook structure at the point of conversion instead of later in the pipeline.

## Features

- Accepts a plain dictionary representing notebook structure.
- Converts the dictionary with `nbformat.from_dict`.
- Validates the resulting notebook object with `nbformat.validate`.
- Returns `notebook_node` on success.
- Returns a structured error payload when conversion or validation fails.

## FAQ

### What input does this tool expect?

It expects a Python dictionary that follows notebook structure conventions such as `nbformat`, `nbformat_minor`, `cells`, and `metadata`.

### Does it return JSON?

No. It returns a `NotebookNode` object in `notebook_node`.

### When should I use this instead of `swarmauri_tool_jupyterreadnotebook`?

Use this package when your notebook starts as in-memory Python data. Use `swarmauri_tool_jupyterreadnotebook` when the notebook already exists on disk.

## Installation

```bash
uv add swarmauri_tool_jupyterfromdict
```

```bash
pip install swarmauri_tool_jupyterfromdict
```

## Usage

```python
from swarmauri_tool_jupyterfromdict import JupyterFromDictTool

payload = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "cells": [],
    "metadata": {},
}

result = JupyterFromDictTool()(notebook_dict=payload)
print(result)
```

## Examples

### Create a notebook node from generated data

```python
result = JupyterFromDictTool()(
    notebook_dict={
        "nbformat": 4,
        "nbformat_minor": 5,
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["# Generated notebook"],
            }
        ],
        "metadata": {},
    }
)

node = result["notebook_node"]
```

### Detect invalid notebook structure

```python
result = JupyterFromDictTool()(
    notebook_dict={"cells": [], "metadata": {}}
)

if "error" in result:
    print(result["error"])
```

## Related Packages

- [`swarmauri_tool_jupytervalidatenotebook`](https://pypi.org/project/swarmauri_tool_jupytervalidatenotebook/)
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
