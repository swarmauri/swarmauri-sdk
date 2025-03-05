
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupytergetiopubmessage/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupytergetiopubmessage" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_jupytergetiopubmessage/README.md">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_tool_jupytergetiopubmessage/README.md&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
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

Below is a brief example of how to use JupyterGetIOPubMessageTool to capture messages from an active Jupyter kernel. In most scenarios, you will have a running Jupyter kernel and a kernel client available.

--------------------------------------------------------------------------------
Example usage:

from jupyter_client import KernelManager
from swarmauri_tool_jupytergetiopubmessage import JupyterGetIOPubMessageTool

# Initialize a new Jupyter kernel
km = KernelManager()
km.start_kernel()
kc = km.client()
kc.start_channels()

# Execute a sample command in the kernel to produce some output
kc.execute("print('Hello from the kernel!')")

# Initialize and use the JupyterGetIOPubMessageTool
tool = JupyterGetIOPubMessageTool()
result = tool(kernel_client=kc, timeout=3.0)

print("Captured stdout:", result["stdout"])
print("Captured stderr:", result["stderr"])
print("Captured logs:", result["logs"])
print("Execution results:", result["execution_results"])
print("Did timeout occur?:", result["timeout_exceeded"])

# Clean up kernel resources
kc.stop_channels()
km.shutdown_kernel()

--------------------------------------------------------------------------------

This usage example demonstrates how to retrieve stdout messages, stderr messages, logs (including certain non-stream messages), and results from executed cells. The timeout parameter controls how long the tool waits for IOPub messages before returning. If the time is exceeded, "timeout_exceeded" will be True.

## Dependencies

• Python 3.10 to 3.13  
• jupyter_client  
• swarmauri_core (for component registration)  
• swarmauri_base (for the base tool functionality)  

Additional development dependencies (e.g., flake8, pytest) are specified in the pyproject.toml file but not required for basic usage.

## Building & Testing

This package uses Poetry for its build system. You may use any standard Python tooling to install and test in your environment. See above Installation instructions for installing into your project.

---

© 2023 Swarmauri. All rights reserved. This project is licensed under the Apache-2.0 License. Use of this tool is governed by the license conditions included in the repository.
