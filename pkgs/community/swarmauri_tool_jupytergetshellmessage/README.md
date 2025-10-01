![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupytergetshellmessage/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupytergetshellmessage" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupytergetshellmessage/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupytergetshellmessage.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupytergetshellmessage/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupytergetshellmessage" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupytergetshellmessage/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupytergetshellmessage" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupytergetshellmessage/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupytergetshellmessage?label=swarmauri_tool_jupytergetshellmessage&color=green" alt="PyPI - swarmauri_tool_jupytergetshellmessage"/></a>
</p>

---

# Swarmauri Tool Jupyter Get Shell Message

Retrieves shell-channel messages from a running Jupyter kernel using `jupyter_client`.

## Features

- Listens on the Jupyter kernel shell channel and captures raw message dicts.
- Returns a dict containing `messages` or an `error` key.
- Helpful for debugging live kernel communication during automated notebook workflows.

## Prerequisites

- Python 3.10 or newer.
- Access to a running Jupyter kernel (Notebook server, JupyterLab, etc.).
- `jupyter_client` and `websocket-client` (installed automatically).

## Installation

```bash
# pip
pip install swarmauri_tool_jupytergetshellmessage

# poetry
poetry add swarmauri_tool_jupytergetshellmessage

# uv (pyproject-based projects)
uv add swarmauri_tool_jupytergetshellmessage
```

## Quickstart

```python
from swarmauri_tool_jupytergetshellmessage import JupyterGetShellMessageTool

channels_url = "ws://localhost:8888/api/kernels/<kernel-id>/channels"
result = JupyterGetIOPubMessageTool()(channels_url, timeout=5.0)

if "messages" in result:
    for msg in result["messages"]:
        print(msg)
else:
    print("Error:", result.get("error"))
```

## Tips

- Ensure you pass the correct kernel channels URL (including security tokens/cookies if your server requires them).
- Increase `timeout` if you expect long-running cells before shell replies are sent.
- Combine with notebook execution tools to capture both SHELL and IOPub messages for full observability.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
