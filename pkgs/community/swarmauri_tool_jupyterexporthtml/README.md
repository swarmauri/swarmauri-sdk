![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexporthtml/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterexporthtml" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexporthtml/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexporthtml.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexporthtml/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterexporthtml" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexporthtml/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterexporthtml" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexporthtml/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexporthtml?label=swarmauri_tool_jupyterexporthtml&color=green" alt="PyPI - swarmauri_tool_jupyterexporthtml"/></a>
</p>

---

# Swarmauri Tool Jupyter Export HTML

Converts a Jupyter notebook (passed in as JSON) to HTML using nbconvert’s `HTMLExporter` with optional custom templates, CSS, and JavaScript.

## Features

- Accepts notebook data as a JSON string (e.g., from `json.dumps(nbformat.read(...))`).
- Supports optional template, inline CSS, and inline JS injection.
- Returns a dict containing `exported_html` or `error` when conversion fails.

## Prerequisites

- Python 3.10 or newer.
- `nbconvert`, `nbformat`, and Swarmauri base/core packages (installed automatically).

## Installation

```bash
# pip
pip install swarmauri_tool_jupyterexporthtml

# poetry
poetry add swarmauri_tool_jupyterexporthtml

# uv (pyproject-based projects)
uv add swarmauri_tool_jupyterexporthtml
```

## Quickstart

```python
import json
import nbformat
from swarmauri_tool_jupyterexporthtml import JupyterExportHTMLTool

notebook = nbformat.read("notebooks/example.ipynb", as_version=4)
notebook_json = json.dumps(notebook)

exporter = JupyterExportHTMLTool()
response = exporter(
    notebook_json=notebook_json,
    template_file=None,
    extra_css="body { font-family: Arial; }",
    extra_js="console.log('Export complete');",
)

if "exported_html" in response:
    Path("notebooks/example.html").write_text(response["exported_html"], encoding="utf-8")
else:
    print("Error:", response["error"])
```

## Tips

- nbconvert templates let you customize the layout; pass a `.tpl` file to `template_file`.
- Keep `extra_css`/`extra_js` lightweight to avoid bloating the HTML output.
- Combine with notebook execution tools (execute → export → publish) for end-to-end pipelines.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
