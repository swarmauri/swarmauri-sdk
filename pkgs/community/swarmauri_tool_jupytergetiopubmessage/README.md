![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupytergetiopubmessage/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupytergetiopubmessage" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupytergetiopubmessage/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupytergetiopubmessage.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupytergetiopubmessage/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupytergetiopubmessage" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupytergetiopubmessage/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupytergetiopubmessage" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupytergetiopubmessage/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupytergetiopubmessage?label=swarmauri_tool_jupytergetiopubmessage&color=green" alt="PyPI - swarmauri_tool_jupytergetiopubmessage"/></a>
</p>

---

# Swarmauri Tool Jupyter Get IOPub Message

Listens to a Jupyter kernel’s IOPub channel and collects stdout/stderr/log messages for downstream processing.

## Features

- Connects to `/api/kernels/{id}/channels` via websocket.
- Returns a dict containing captured `stdout`, `stderr`, `logs`, `execution_results`, and a `timeout_exceeded` flag.
- Built on `jupyter_client` with Swarmauri tool registration.

## Prerequisites

- Python 3.10 or newer.
- `jupyter_client`, `websocket-client` installed (pulled automatically).
- Access to a running Jupyter kernel (e.g., Notebook server).

## Installation

```bash
# pip
pip install swarmauri_tool_jupytergetiopubmessage

# poetry
poetry add swarmauri_tool_jupytergetiopubmessage

# uv (pyproject-based projects)
uv add swarmauri_tool_jupytergetiopubmessage
```

## Quickstart

```python
from swarmauri_tool_jupytergetiopubmessage import JupyterGetIOPubMessageTool

channels_url = "ws://localhost:8888/api/kernels/<kernel-id>/channels"
result = JupyterGetIOPubMessageTool()(channels_url, timeout=3.0)

print("stdout:", result["stdout"])
print("stderr:", result["stderr"])
print("logs:", result["logs"])
print("timeout?", result["timeout_exceeded"])
```

## Tips

- Use alongside execution tools to capture live output during automated notebook runs.
- Ensure your environment handles Jupyter tokens/cookies if the server requires authentication.
- Increase `timeout` for longer-running cells to collect all outputs before returning.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
