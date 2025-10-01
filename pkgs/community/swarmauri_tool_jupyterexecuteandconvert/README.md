![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecuteandconvert/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterexecuteandconvert" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecuteandconvert/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecuteandconvert.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecuteandconvert/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterexecuteandconvert" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecuteandconvert/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterexecuteandconvert" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecuteandconvert/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexecuteandconvert?label=swarmauri_tool_jupyterexecuteandconvert&color=green" alt="PyPI - swarmauri_tool_jupyterexecuteandconvert"/></a>
</p>

---

# Swarmauri Tool Jupyter Execute & Convert

Executes a Jupyter notebook and converts the output to HTML or PDF using nbconvert—packaged as a Swarmauri tool.

## Features

- Runs notebooks with configurable execution timeout.
- Converts executed notebooks to `html` or `pdf` via nbconvert.
- Returns a status dictionary with the converted file path or error details.

## Prerequisites

- Python 3.10 or newer.
- `nbconvert`, `nbformat`, and Jupyter runtime (installed automatically).
- Notebook dependencies must be available in the execution environment.

## Installation

```bash
# pip
pip install swarmauri_tool_jupyterexecuteandconvert

# poetry
poetry add swarmauri_tool_jupyterexecuteandconvert

# uv (pyproject-based projects)
uv add swarmauri_tool_jupyterexecuteandconvert
```

## Quickstart

```python
from swarmauri_tool_jupyterexecuteandconvert import JupyterExecuteAndConvertTool

tool = JupyterExecuteAndConvertTool()
response = tool(
    notebook_path="notebooks/analysis.ipynb",
    output_format="pdf",
    execution_timeout=600,
)

if response.get("status") == "success":
    print("Converted file:", response["converted_file"])
else:
    print("Error:", response.get("error"))
    print("Message:", response.get("message"))
```

## Tips

- Set `execution_timeout` high enough for long-running notebooks; nbconvert defaults to 600 seconds.
- Ensure notebooks run headlessly: avoid widgets or interactive inputs that pause execution.
- Install LaTeX (`tectonic`, `texlive`) if exporting to PDF on systems where nbconvert requires it.
- Combine with `JupyterClearOutputTool` to strip outputs after conversion if you want clean notebooks and rich artifacts.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
