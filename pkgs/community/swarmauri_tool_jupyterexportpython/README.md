![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_jupyterexportpython/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_jupyterexportpython/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexportpython/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexportpython.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexportpython/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexportpython/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterexportpython" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexportpython/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexportpython?label=swarmauri_tool_jupyterexportpython&color=green" alt="PyPI - swarmauri_tool_jupyterexportpython"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Jupyter Export Python Tool

`swarmauri_tool_jupyterexportpython` converts notebook objects into Python scripts through `nbconvert.PythonExporter`, making it useful for code extraction, audit, and migration workflows.

## Why

- Extract runnable Python from notebooks for review or reuse.
- Bridge notebook prototypes into script-based workflows.
- Keep notebook-to-script export inside a Swarmauri tool interface.

## Features

- Accepts notebook objects compatible with `nbconvert`.
- Exports Python source through `nbconvert.PythonExporter`.
- Supports optional custom templates.
- Returns the generated script as a string.
- Returns a structured error payload on export failure.

## FAQ

### Does this package write a `.py` file?

No. It returns the exported script text in `exported_script`.

### What kind of input does it expect?

It expects a notebook object, not a file path and not a JSON string.

### When should I use a custom template?

Use a custom template when you need a specific script layout, preamble, or code-cell transformation strategy.

## Installation

```bash
uv add swarmauri_tool_jupyterexportpython
```

```bash
pip install swarmauri_tool_jupyterexportpython
```

## Usage

```python
from swarmauri_tool_jupyterexportpython import JupyterExportPythonTool

notebook = {
    "cells": [{"cell_type": "code", "metadata": {}, "source": "print('hello')", "outputs": []}],
    "metadata": {},
    "nbformat": 4,
    "nbformat_minor": 5,
}

result = JupyterExportPythonTool()(notebook=notebook)
print(result["exported_script"])
```

## Examples

### Export a notebook to Python

```python
result = JupyterExportPythonTool()(notebook=notebook)
script = result["exported_script"]
```

### Export with a custom template

```python
result = JupyterExportPythonTool()(
    notebook=notebook,
    template_file="templates/python-export.tpl",
)
```

## Related Packages

- [`swarmauri_tool_jupyterexporthtml`](https://pypi.org/project/swarmauri_tool_jupyterexporthtml/)
- [`swarmauri_tool_jupyterexportmarkdown`](https://pypi.org/project/swarmauri_tool_jupyterexportmarkdown/)
- [`swarmauri_tool_jupyterexportlatex`](https://pypi.org/project/swarmauri_tool_jupyterexportlatex/)
- [`swarmauri_tool_jupyterreadnotebook`](https://pypi.org/project/swarmauri_tool_jupyterreadnotebook/)
- [`swarmauri_tool_jupyterwritenotebook`](https://pypi.org/project/swarmauri_tool_jupyterwritenotebook/)

## Foundational Swarmauri Packages

- [`swarmauri`](https://pypi.org/project/swarmauri/)
- [`swarmauri_core`](https://pypi.org/project/swarmauri_core/)
- [`swarmauri_base`](https://pypi.org/project/swarmauri_base/)
- [`swarmauri_standard`](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)
- [nbconvert Python exporter docs](https://nbconvert.readthedocs.io/)
- [Jupyter documentation](https://jupyter.org/documentation)
