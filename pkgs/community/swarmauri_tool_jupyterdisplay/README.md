![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterdisplay/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterdisplay" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterdisplay/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterdisplay.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterdisplay/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterdisplay" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterdisplay/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterdisplay" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterdisplay/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterdisplay?label=swarmauri_tool_jupyterdisplay&color=green" alt="PyPI - swarmauri_tool_jupyterdisplay"/></a>
</p>

---

# Swarmauri Tool Jupyter Display

Tool for displaying text, HTML, images, or LaTeX in a Jupyter notebook using IPython's rich display helpers.

## Features

- Accepts `data` and optional `data_format` (`auto`, `text`, `html`, `image`, `latex`).
- Uses `IPython.display` to render the appropriate representation.
- Returns a status dictionary indicating success or failure.

## Prerequisites

- Python 3.10 or newer.
- Running inside a Jupyter notebook or environment that supports IPython display.
- `IPython` installed (pulled in automatically).

## Installation

```bash
# pip
pip install swarmauri_tool_jupyterdisplay

# poetry
poetry add swarmauri_tool_jupyterdisplay

# uv (pyproject-based projects)
uv add swarmauri_tool_jupyterdisplay
```

## Quickstart

```python
from swarmauri_tool_jupyterdisplay import JupyterDisplayTool

display_tool = JupyterDisplayTool()
print(display_tool("<b>Hello, world!</b>", data_format="html"))
```

## Displaying Images

```python
from swarmauri_tool_jupyterdisplay import JupyterDisplayTool

image_path = "plots/chart.png"
JupyterDisplayTool()(image_path, data_format="image")
```

## Tips

- Use `data_format="auto"` (default) to treat the data as Markdown text.
- Provide absolute or notebook-relative paths for images when using `data_format="image"`.
- Wrap calls in Swarmauri tool chains to render results (e.g., charts, HTML reports) inline during agent runs.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
