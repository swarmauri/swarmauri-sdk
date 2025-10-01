![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterruncell/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterruncell" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterruncell/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterruncell.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterruncell/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterruncell" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterruncell/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterruncell" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterruncell/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterruncell?label=swarmauri_tool_jupyterruncell&color=green" alt="PyPI - swarmauri_tool_jupyterruncell"/></a>
</p>

---

# Swarmauri Tool Jupyter Run Cell

Executes a code string inside the current IPython kernel and captures stdout/stderr/error text.

## Features

- Runs arbitrary Python snippets with optional timeout.
- Returns `success`, `cell_output`, and `error_output` keys.
- Designed for use inside running notebooks or IPython sessions.

## Prerequisites

- Python 3.10 or newer.
- Running within IPython/Jupyter environment.

## Installation

```bash
# pip
pip install swarmauri_tool_jupyterruncell

# poetry
poetry add swarmauri_tool_jupyterruncell

# uv (pyproject-based projects)
uv add swarmauri_tool_jupyterruncell
```

## Quickstart

```python
from swarmauri_tool_jupyterruncell import JupyterRunCellTool

runner = JupyterRunCellTool()
result = runner(code="print('Hello from Swarmauri!')", timeout=5)

if result["success"]:
    print("stdout:", result["cell_output"])
else:
    print("error:", result["error_output"])
```

## Tips

- Set `timeout=0` (or omit) to disable execution timeouts.
- Capture `error_output` to diagnose exceptions raised by the executed code.
- Use alongside other notebook automation tools (execute, export, etc.) to build richer pipelines.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
