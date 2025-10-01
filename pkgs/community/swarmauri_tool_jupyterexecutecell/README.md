![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutecell/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterexecutecell" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecutecell/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecutecell.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutecell/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterexecutecell" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutecell/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterexecutecell" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutecell/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexecutecell?label=swarmauri_tool_jupyterexecutecell&color=green" alt="PyPI - swarmauri_tool_jupyterexecutecell"/></a>
</p>

---

# Swarmauri Tool Jupyter Execute Cell

Executes Python code in the active Jupyter kernel and captures stdout/stderr/errors for downstream tooling.

## Features

- Accepts raw code strings and optionally a timeout.
- Returns a dict with `stdout`, `stderr`, and `error` keys.
- Built on `jupyter_client` to talk to the running kernel.

## Prerequisites

- Python 3.10 or newer.
- Jupyter kernel running in the environment (IPython/Jupyter installed).

## Installation

```bash
# pip
pip install swarmauri_tool_jupyterexecutecell

# poetry
poetry add swarmauri_tool_jupyterexecutecell

# uv (pyproject-based projects)
uv add swarmauri_tool_jupyterexecutecell
```

## Quickstart

```python
from swarmauri_tool_jupyterexecutecell import JupyterExecuteCellTool

code = "print('Hello from Swarmauri!')"
result = JupyterExecuteCellTool()(code, timeout=60)

print("stdout:", result["stdout"])
print("stderr:", result["stderr"])
print("error:", result["error"])
```

## Tips

- Increase `timeout` for cells that perform long-running tasks.
- The tool executes in the current kernel—make sure dependencies are already imported/installed in that environment.
- Handle errors gracefully by checking the `error` field before using results.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
