![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexportpython/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterexportpython" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexportpython/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexportpython.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexportpython/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterexportpython" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexportpython/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterexportpython" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexportpython/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexportpython?label=swarmauri_tool_jupyterexportpython&color=green" alt="PyPI - swarmauri_tool_jupyterexportpython"/></a>
</p>

---

# Swarmauri Tool Jupyter Export Python

Exports a Jupyter `NotebookNode` to a Python script using nbconvert’s `PythonExporter` with optional custom templates.

## Features

- Accepts a notebook object (`nbformat.NotebookNode`) and returns the rendered `.py` source.
- Supports passing an nbconvert template for custom formatting.
- Returns `{"exported_script": ...}` on success or `{"error": ...}` on failure.

## Prerequisites

- Python 3.10 or newer.
- nbconvert/nbformat installed (pulled automatically).

## Installation

```bash
# pip
pip install swarmauri_tool_jupyterexportpython

# poetry
poetry add swarmauri_tool_jupyterexportpython

# uv (pyproject-based projects)
uv add swarmauri_tool_jupyterexportpython
```

## Quickstart

```python
import nbformat
from swarmauri_tool_jupyterexportpython import JupyterExportPythonTool

notebook = nbformat.read("notebooks/example.ipynb", as_version=4)
exporter = JupyterExportPythonTool()
result = exporter(notebook, template_file=None)

if "exported_script" in result:
    Path("notebooks/example.py").write_text(result["exported_script"], encoding="utf-8")
else:
    print("Error:", result["error"])
```

## Tips

- Use custom templates to control cell separators or code comments—pass a `.tpl` file via `template_file`.
- Pair with notebook execution tools (execute → export to .py) to operationalize notebooks as Python scripts.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
