![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_jupyterexportlatex/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_jupyterexportlatex/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexportlatex/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexportlatex.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexportlatex/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexportlatex/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterexportlatex" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexportlatex/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexportlatex?label=swarmauri_tool_jupyterexportlatex&color=green" alt="PyPI - swarmauri_tool_jupyterexportlatex"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Jupyter Export LaTeX Tool

`swarmauri_tool_jupyterexportlatex` converts a notebook object into LaTeX with `nbconvert.LatexExporter` and can optionally generate a PDF artifact. It also supports custom LaTeX templates for publication-oriented workflows.

## Why

- Produce LaTeX artifacts from notebooks for academic and report-generation workflows.
- Reuse custom templates for publication formatting.
- Optionally bridge notebook output into PDF-ready artifacts from a single tool surface.

## Features

- Accepts notebook objects and normalizes them before export.
- Exports LaTeX with `nbconvert.LatexExporter`.
- Supports custom template directories and files.
- Optionally generates PDF output.
- Falls back to a dummy PDF artifact when `xelatex` is unavailable in the local environment.

## FAQ

### What input does this tool expect?

It expects a notebook object compatible with `nbformat.from_dict`, not a JSON string and not a notebook file path.

### Does it always generate a PDF?

No. PDF generation happens only when `to_pdf=True`.

### What happens if `xelatex` is missing?

The tool creates a dummy PDF file for testable fallback behavior instead of failing immediately.

## Installation

```bash
uv add swarmauri_tool_jupyterexportlatex
```

```bash
pip install swarmauri_tool_jupyterexportlatex
```

## Usage

```python
from swarmauri_tool_jupyterexportlatex import JupyterExportLatexTool

notebook = {
    "cells": [{"cell_type": "code", "metadata": {}, "source": ["1 + 1"], "outputs": []}],
    "metadata": {},
    "nbformat": 4,
    "nbformat_minor": 5,
}

result = JupyterExportLatexTool()(
    notebook_node=notebook,
    to_pdf=False,
)

print(result["latex_content"][:200])
```

## Examples

### Export LaTeX only

```python
result = JupyterExportLatexTool()(
    notebook_node=notebook,
    use_custom_template=False,
    to_pdf=False,
)
```

### Export LaTeX and request PDF output

```python
result = JupyterExportLatexTool()(
    notebook_node=notebook,
    to_pdf=True,
)

print(result.get("pdf_file_path"))
```

## Related Packages

- [`swarmauri_tool_jupyterexporthtml`](https://pypi.org/project/swarmauri_tool_jupyterexporthtml/)
- [`swarmauri_tool_jupyterexportmarkdown`](https://pypi.org/project/swarmauri_tool_jupyterexportmarkdown/)
- [`swarmauri_tool_jupyterexportpython`](https://pypi.org/project/swarmauri_tool_jupyterexportpython/)
- [`swarmauri_tool_jupyterexecuteandconvert`](https://pypi.org/project/swarmauri_tool_jupyterexecuteandconvert/)
- [`swarmauri_tool_jupyterexecutenotebook`](https://pypi.org/project/swarmauri_tool_jupyterexecutenotebook/)

## Foundational Swarmauri Packages

- [`swarmauri`](https://pypi.org/project/swarmauri/)
- [`swarmauri_core`](https://pypi.org/project/swarmauri_core/)
- [`swarmauri_base`](https://pypi.org/project/swarmauri_base/)
- [`swarmauri_standard`](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)
- [nbconvert LaTeX export docs](https://nbconvert.readthedocs.io/)
- [Jupyter documentation](https://jupyter.org/documentation)
