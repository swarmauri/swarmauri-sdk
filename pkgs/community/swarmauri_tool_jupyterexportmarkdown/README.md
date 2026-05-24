![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_jupyterexportmarkdown/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_jupyterexportmarkdown/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexportmarkdown/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexportmarkdown.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexportmarkdown/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexportmarkdown/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterexportmarkdown" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexportmarkdown/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexportmarkdown?label=swarmauri_tool_jupyterexportmarkdown&color=green" alt="PyPI - swarmauri_tool_jupyterexportmarkdown"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Jupyter Export Markdown Tool

`swarmauri_tool_jupyterexportmarkdown` converts a Jupyter notebook dictionary into Markdown using `nbconvert.MarkdownExporter`, with optional template selection and inline style resources for static publishing workflows.

## Why

- Convert notebooks into documentation-friendly Markdown.
- Feed notebook output into static-site, docs, and content pipelines.
- Keep notebook-to-Markdown generation inside a Swarmauri tool interface.

## Features

- Accepts notebook content as a Python dictionary.
- Normalizes list-based cell sources before export.
- Exports with `nbconvert.MarkdownExporter`.
- Supports optional custom templates.
- Supports optional style resources for embedded export customization.

## FAQ

### What kind of input does this tool expect?

It expects a JSON-like Python dictionary representing a notebook, not a raw file path and not a JSON string.

### Does it write a `.md` file?

No. It returns Markdown content in `exported_markdown`.

### What is the `styles` argument for?

It lets callers pass style content into the nbconvert resources structure for custom Markdown export workflows.

## Installation

```bash
uv add swarmauri_tool_jupyterexportmarkdown
```

```bash
pip install swarmauri_tool_jupyterexportmarkdown
```

## Usage

```python
from swarmauri_tool_jupyterexportmarkdown import JupyterExportMarkdownTool

notebook = {
    "cells": [
        {"cell_type": "markdown", "metadata": {}, "source": ["# Demo"]},
        {
            "cell_type": "code",
            "metadata": {},
            "execution_count": None,
            "outputs": [],
            "source": ["print('hello')"],
        },
    ],
    "metadata": {},
    "nbformat": 4,
    "nbformat_minor": 5,
}

result = JupyterExportMarkdownTool()(notebook_json=notebook)
print(result["exported_markdown"])
```

## Examples

### Export Markdown with a custom template

```python
result = JupyterExportMarkdownTool()(
    notebook_json=notebook,
    template="lab",
)
```

### Export Markdown with custom styles

```python
result = JupyterExportMarkdownTool()(
    notebook_json=notebook,
    styles="pre { font-size: 0.9rem; }",
)
```

## Related Packages

- [`swarmauri_tool_jupyterexporthtml`](https://pypi.org/project/swarmauri_tool_jupyterexporthtml/)
- [`swarmauri_tool_jupyterexportlatex`](https://pypi.org/project/swarmauri_tool_jupyterexportlatex/)
- [`swarmauri_tool_jupyterexportpython`](https://pypi.org/project/swarmauri_tool_jupyterexportpython/)
- [`swarmauri_tool_jupyterexecuteandconvert`](https://pypi.org/project/swarmauri_tool_jupyterexecuteandconvert/)
- [`swarmauri_tool_jupyterreadnotebook`](https://pypi.org/project/swarmauri_tool_jupyterreadnotebook/)

## Foundational Swarmauri Packages

- [`swarmauri`](https://pypi.org/project/swarmauri/)
- [`swarmauri_core`](https://pypi.org/project/swarmauri_core/)
- [`swarmauri_base`](https://pypi.org/project/swarmauri_base/)
- [`swarmauri_standard`](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)
- [nbconvert Markdown exporter docs](https://nbconvert.readthedocs.io/)
- [Jupyter documentation](https://jupyter.org/documentation)
