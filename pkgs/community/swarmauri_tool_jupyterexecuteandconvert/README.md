![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_jupyterexecuteandconvert/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_jupyterexecuteandconvert/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecuteandconvert/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecuteandconvert.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecuteandconvert/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecuteandconvert/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterexecuteandconvert" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecuteandconvert/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexecuteandconvert?label=swarmauri_tool_jupyterexecuteandconvert&color=green" alt="PyPI - swarmauri_tool_jupyterexecuteandconvert"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Jupyter Execute And Convert Tool

`swarmauri_tool_jupyterexecuteandconvert` runs a notebook through the `jupyter nbconvert` CLI, writes an executed notebook artifact, and then converts that executed notebook to a target output format such as HTML or PDF.

## Why

- Execute notebooks and publish rendered artifacts in one Swarmauri tool call.
- Keep notebook reporting workflows inside a simple automation surface.
- Produce web or document outputs from the exact executed notebook state.

## Features

- Verifies the source notebook exists before execution.
- Executes notebooks with `jupyter nbconvert --execute`.
- Converts the executed notebook in a second `nbconvert` step.
- Supports `html` and `pdf` output formats.
- Returns either `{"converted_file": ..., "status": "success"}` or an error payload.

## FAQ

### What file does this tool convert?

It first creates an executed notebook named `executed_<original>.ipynb`, then converts that executed notebook to the requested format.

### Does this return notebook content?

No. It returns metadata about the produced converted file, not the notebook object itself.

### When should I use this instead of `swarmauri_tool_jupyterexecutenotebook`?

Use this package when you want rendered artifacts like HTML or PDF. Use `swarmauri_tool_jupyterexecutenotebook` when you want the executed `NotebookNode` in memory.

## Installation

```bash
uv add swarmauri_tool_jupyterexecuteandconvert
```

```bash
pip install swarmauri_tool_jupyterexecuteandconvert
```

## Usage

```python
from swarmauri_tool_jupyterexecuteandconvert import JupyterExecuteAndConvertTool

tool = JupyterExecuteAndConvertTool()
result = tool(
    notebook_path="reports/weekly.ipynb",
    output_format="html",
    execution_timeout=300,
)

print(result)
```

## Examples

### Execute a notebook and export HTML

```python
response = JupyterExecuteAndConvertTool()(
    notebook_path="reports/status.ipynb",
    output_format="html",
    execution_timeout=120,
)

print(response["converted_file"])
```

### Execute a notebook and export PDF

```python
response = JupyterExecuteAndConvertTool()(
    notebook_path="reports/board_packet.ipynb",
    output_format="pdf",
    execution_timeout=600,
)

if "error" in response:
    print(response["message"])
```

## Related Packages

- [`swarmauri_tool_jupyterexecutenotebook`](https://pypi.org/project/swarmauri_tool_jupyterexecutenotebook/)
- [`swarmauri_tool_jupyterexecutenotebookwithparameters`](https://pypi.org/project/swarmauri_tool_jupyterexecutenotebookwithparameters/)
- [`swarmauri_tool_jupyterexporthtml`](https://pypi.org/project/swarmauri_tool_jupyterexporthtml/)
- [`swarmauri_tool_jupyterexportlatex`](https://pypi.org/project/swarmauri_tool_jupyterexportlatex/)
- [`swarmauri_tool_jupyterexportpython`](https://pypi.org/project/swarmauri_tool_jupyterexportpython/)

## Foundational Swarmauri Packages

- [`swarmauri`](https://pypi.org/project/swarmauri/)
- [`swarmauri_core`](https://pypi.org/project/swarmauri_core/)
- [`swarmauri_base`](https://pypi.org/project/swarmauri_base/)
- [`swarmauri_standard`](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)
- [nbconvert documentation](https://nbconvert.readthedocs.io/)
- [Jupyter documentation](https://jupyter.org/documentation)
