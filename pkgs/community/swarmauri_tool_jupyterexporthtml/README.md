![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_jupyterexporthtml/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_jupyterexporthtml/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexporthtml/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexporthtml.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexporthtml/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexporthtml/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterexporthtml" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexporthtml/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexporthtml?label=swarmauri_tool_jupyterexporthtml&color=green" alt="PyPI - swarmauri_tool_jupyterexporthtml"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Jupyter Export HTML Tool

`swarmauri_tool_jupyterexporthtml` converts Jupyter notebook JSON into HTML using `nbconvert.HTMLExporter`, with optional template selection and inline CSS or JavaScript injection.

## Why

- Publish notebooks as web-ready HTML artifacts.
- Apply presentation-specific HTML templates without rewriting notebook content.
- Add inline CSS or JavaScript for branded notebook presentation workflows.

## Features

- Parses notebook JSON into a `NotebookNode`.
- Exports notebook content through `nbconvert.HTMLExporter`.
- Supports optional `template_file` overrides.
- Can inject inline CSS into the document head.
- Can inject inline JavaScript before the closing body tag.

## FAQ

### What input does this tool accept?

It expects a JSON string representing the notebook, not a file path and not a Python dictionary.

### Does it write an HTML file?

No. It returns the generated HTML string in `exported_html`.

### When should I use extra CSS or extra JS?

Use them when the exported notebook needs lightweight presentation customization without managing a full custom exporter package.

## Installation

```bash
uv add swarmauri_tool_jupyterexporthtml
```

```bash
pip install swarmauri_tool_jupyterexporthtml
```

## Usage

```python
from swarmauri_tool_jupyterexporthtml import JupyterExportHtmlTool

notebook_json = """
{
  "cells": [{"cell_type": "markdown", "metadata": {}, "source": ["# Demo"]}],
  "metadata": {},
  "nbformat": 4,
  "nbformat_minor": 5
}
"""

tool = JupyterExportHtmlTool()
result = tool(notebook_json=notebook_json)

print(result["exported_html"][:200])
```

## Examples

### Export HTML with custom CSS

```python
result = JupyterExportHtmlTool()(
    notebook_json=notebook_json,
    extra_css="body { max-width: 960px; margin: 0 auto; }",
)

html = result["exported_html"]
```

### Export HTML with custom JavaScript

```python
result = JupyterExportHtmlTool()(
    notebook_json=notebook_json,
    extra_js="console.log('Notebook rendered');",
)
```

## Related Packages

- [`swarmauri_tool_jupyterexecuteandconvert`](https://pypi.org/project/swarmauri_tool_jupyterexecuteandconvert/)
- [`swarmauri_tool_jupyterexportmarkdown`](https://pypi.org/project/swarmauri_tool_jupyterexportmarkdown/)
- [`swarmauri_tool_jupyterexportlatex`](https://pypi.org/project/swarmauri_tool_jupyterexportlatex/)
- [`swarmauri_tool_jupyterexportpython`](https://pypi.org/project/swarmauri_tool_jupyterexportpython/)
- [`swarmauri_tool_jupyterexecutenotebook`](https://pypi.org/project/swarmauri_tool_jupyterexecutenotebook/)

## Foundational Swarmauri Packages

- [`swarmauri`](https://pypi.org/project/swarmauri/)
- [`swarmauri_core`](https://pypi.org/project/swarmauri_core/)
- [`swarmauri_base`](https://pypi.org/project/swarmauri_base/)
- [`swarmauri_standard`](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)
- [nbconvert HTMLExporter docs](https://nbconvert.readthedocs.io/en/latest/usage.html)
- [Jupyter documentation](https://jupyter.org/documentation)
