
![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

A dedicated Python package providing a tool to retrieve shell messages from a running Jupyter kernel using jupyter_client. Built on the swarmauri framework, JupyterGetShellMessageTool is suitable for debugging, logging, and diagnostic purposes.

---

## Installation

To install this package from PyPI, use the following command:

    pip install swarmauri_tool_jupytergetshellmessage

If you are using Poetry for dependency management, add it to your project by specifying the package name in your pyproject.toml under [tool.poetry.dependencies]:

    [tool.poetry.dependencies]
    swarmauri_tool_jupytergetshellmessage = "^0.1.0.dev1"

Once installed, the package automatically brings in its required dependencies:
• swarmauri_core  
• swarmauri_base  
• jupyter_client  

No specialized steps beyond a standard Python environment with pip or Poetry are necessary.

---

## Usage

Below is a simple example illustrating how to retrieve shell messages from a currently running Jupyter kernel. Make sure you have an active Jupyter kernel in the environment you are running this code from (for instance, a notebook server launched via "jupyter notebook" or "jupyter lab").

1. Import JupyterGetShellMessageTool:

    from swarmauri_tool_jupytergetshellmessage import JupyterGetShellMessageTool

2. Instantiate the tool and call it:

    tool = JupyterGetShellMessageTool()
    result = tool(timeout=10.0)  # Wait up to 10 seconds for shell messages

3. Inspect the result:

    if "messages" in result:
        for msg in result["messages"]:
            print("Shell Message:", msg)
    else:
        print("No messages or error:", result.get("error", "No details"))

The tool attempts to connect to the active Jupyter kernel, retrieve available shell messages, and return them in a structured dictionary. If no messages are found within the specified timeout, it returns an error message indicating the timeout event.

---

## Dependencies

• swarmauri_core and swarmauri_base provide the core classes (ComponentBase, ToolBase) for building and integrating tools across the swarmauri ecosystem.  
• jupyter_client is leveraged to interface with the running Jupyter kernel, enabling retrieval of shell-based IPC messages.  

These dependencies are automatically installed when installing this package via pip or Poetry.

---

## Contributing

Issues and feature requests for swarmauri_tool_jupytergetshellmessage are always welcome. Although direct repository interaction details are not included here, feel free to suggest improvements or report problems using the relevant issue tracker.

---

© 2023 Swarmauri. Licensed under the Apache License, Version 2.0.  
See the LICENSE file for details.
