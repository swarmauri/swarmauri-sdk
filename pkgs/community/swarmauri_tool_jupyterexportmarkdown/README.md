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

# Swarmauri Tool Jupyter Export Markdown

Converts a Jupyter `NotebookNode` to Markdown using nbconvertâ€™s `MarkdownExporter`. Injectable CSS and JS snippets let you tweak the output for static publishing.

## Features

- Accepts a notebook JSON string and returns rendered Markdown.
- Optional inline CSS/JS injection to customize the exported document.
- Returns a dict with `exported_markdown` or `error` if conversion fails.

## Prerequisites

- Python 3.10 or newer.
- nbconvert/nbformat installed (pulled in automatically).

## Installation

```bash
# pip
pip install swarmauri_tool_jupyterexportmarkdown

# poetry
poetry add swarmauri_tool_jupyterexportmarkdown

# uv (pyproject-based projects)
uv add swarmauri_tool_jupyterexportmarkdown
```

## Quickstart

```python
import json
import nbformat
from swarmauri_tool_jupyterexportmarkdown import JupyterExportMarkdownTool

notebook = nbformat.read("notebooks/example.ipynb", as_version=4)
notebook_json = json.dumps(notebook)

exporter = JupyterExportMarkdownTool()
response = exporter(
    notebook_json=notebook_json,
    extra_css="blockquote { color: gray; }",
    extra_js="console.log('Markdown ready');",
)

if "exported_markdown" in response:
    Path("notebooks/example.md").write_text(response["exported_markdown"], encoding="utf-8")
else:
    print("Error:", response["error"])
```

## Tips

- Use Markdown export when preparing notebooks for static docs, blogs, or README content.
- Apply lightweight CSS/JS to adjust styling when the Markdown is embedded in HTML environments.
- Combine with notebook execution tools to build pipelines (execute â†’ convert to Markdown â†’ publish).

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.


