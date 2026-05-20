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
</p>

# Swarmauri Tool Jupyter Export LaTeX

Converts a Jupyter `NotebookNode` into LaTeX using nbconvert; optionally generates a PDF.

## Features

- Uses nbconvertâ€™s `LatexExporter` with optional custom template support.
- Returns the LaTeX string and (optionally) the path to a generated PDF.
- Accepts inline CSS/JS injection via nbconvert hooks.

## Prerequisites

- Python 3.10 or newer.
- nbconvert (with LaTeX/PDF dependencies such as TeXLive or Tectonic if generating PDFs).
- Swarmauri base/core packages (installed automatically).

## Installation

```bash
# pip
pip install swarmauri_tool_jupyterexportlatex

# poetry
poetry add swarmauri_tool_jupyterexportlatex

# uv (pyproject-based projects)
uv add swarmauri_tool_jupyterexportlatex
```

## Quickstart

```python
import json
import nbformat
from swarmauri_tool_jupyterexportlatex import JupyterExportLatexTool

notebook = nbformat.read("notebooks/example.ipynb", as_version=4)
exporter = JupyterExportLatexTool()
response = exporter(
    notebook_node=notebook,
    use_custom_template=False,
    template_path=None,
    to_pdf=True,
)

if "latex_content" in response:
    Path("notebooks/example.tex").write_text(response["latex_content"], encoding="utf-8")

if pdf := response.get("pdf_file_path"):
    print("PDF saved to", pdf)
else:
    print("Error:", response.get("error"))
```

## Tips

- Install a TeX distribution (e.g., `texlive`, `tectonic`) when `to_pdf=True`.
- Use `use_custom_template=True` and `template_path` to control the LaTeX layout.
- Combine with notebook execution tools (execute â†’ export â†’ PDF) for reporting pipelines.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
