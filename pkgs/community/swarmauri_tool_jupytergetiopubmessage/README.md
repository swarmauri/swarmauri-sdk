
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

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

# Swarmauri Tool Jupyter Get IO PubMessage

A Python tool designed to retrieve messages from the IOPub channel of a Jupyter kernel using jupyter_client, capturing cell outputs, logging information, and errors.

## Installation

To install swarmauri_tool_jupytergetiopubmessage, make sure you have Python 3.10 or later. You can install the latest release from PyPI using:

  pip install swarmauri_tool_jupytergetiopubmessage

Verify the installation by opening a Python shell and importing the module:

  python
  >>> import swarmauri_tool_jupytergetiopubmessage
  >>> print(swarmauri_tool_jupytergetiopubmessage.__version__)
  '0.1.0.dev1'

If you see a valid version number, the package is installed and ready to use.

## Usage

Below is a brief example of how to use ``JupyterGetIOPubMessageTool`` to capture
messages from an active Jupyter kernel. The tool expects the WebSocket URL for
the kernel's ``/api/kernels/{id}/channels`` endpoint.

--------------------------------------------------------------------------------
Example usage:

from swarmauri_tool_jupytergetiopubmessage import JupyterGetIOPubMessageTool

# URL to the running kernel's channels endpoint
channels_url = "ws://localhost:8888/api/kernels/12345/channels"

# Initialize and use the tool
tool = JupyterGetIOPubMessageTool()
result = tool(channels_url, timeout=3.0)

print("Captured stdout:", result["stdout"])
print("Captured stderr:", result["stderr"])
print("Captured logs:", result["logs"])
print("Execution results:", result["execution_results"])
print("Did timeout occur?:", result["timeout_exceeded"])


--------------------------------------------------------------------------------

This usage example demonstrates how to retrieve stdout messages, stderr messages, logs (including certain non-stream messages), and results from executed cells. The timeout parameter controls how long the tool waits for IOPub messages before returning. If the time is exceeded, "timeout_exceeded" will be True.

## Dependencies

• Python 3.10 to 3.13
• websocket-client
• jupyter_client
• swarmauri_core (for component registration)
• swarmauri_base (for the base tool functionality)

Additional development dependencies (e.g., flake8, pytest) are specified in the pyproject.toml file but not required for basic usage.

## Building & Testing

This package uses Poetry for its build system. You may use any standard Python tooling to install and test in your environment. See above Installation instructions for installing into your project.

---

© 2023 Swarmauri. All rights reserved. This project is licensed under the Apache-2.0 License. Use of this tool is governed by the license conditions included in the repository.
