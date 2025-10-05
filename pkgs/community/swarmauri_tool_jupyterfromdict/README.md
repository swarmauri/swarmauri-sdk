![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterfromdict/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterfromdict" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterfromdict/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterfromdict.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterfromdict/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterfromdict" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterfromdict/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterfromdict" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterfromdict/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterfromdict?label=swarmauri_tool_jupyterfromdict&color=green" alt="PyPI - swarmauri_tool_jupyterfromdict"/></a>
</p>

---

# Swarmauri Tool Jupyter From Dict

Creates a validated Jupyter `NotebookNode` from a Python dictionary using nbformat.

## Features

- Validates notebook structure against nbformat schema.
- Returns `{"notebook_node": ...}` on success or `{"error": ...}` when conversion fails.
- Useful for programmatically building notebooks before executing/exporting them with other Swarmauri tools.

## Prerequisites

- Python 3.10 or newer.
- nbformat installed (pulled automatically).

## Installation

```bash
# pip
pip install swarmauri_tool_jupyterfromdict

# poetry
poetry add swarmauri_tool_jupyterfromdict

# uv (pyproject-based projects)
uv add swarmauri_tool_jupyterfromdict
```

## Quickstart

```python
import json
from swarmauri_tool_jupyterfromdict import JupyterFromDictTool

notebook_dict = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {},
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["# Hello World\n", "This is a generated notebook."],
        }
    ],
}

result = JupyterFromDictTool()(notebook_dict)
if "notebook_node" in result:
    print("NotebookNode ready", type(result["notebook_node"]))
else:
    print("Error:", result["error"])
```

## Tips

- Feed the resulting `NotebookNode` directly into execution/export tools such as `JupyterExecuteNotebookTool` or nbconvert exporters.
- Use `json.dumps`/`json.loads` if you need to persist or transmit the notebook dictionary before conversion.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
