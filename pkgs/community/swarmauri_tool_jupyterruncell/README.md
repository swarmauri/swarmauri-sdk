
![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

This package provides a specialized tool for executing Python code cells interactively, capturing output and errors, and optionally applying timeouts. It is designed to integrate seamlessly with the broader Swarmauri tool ecosystem.

## Installation

To install the package from PyPI:

1. Make sure you have Python 3.10 or newer.
2. Install using pip:

   pip install swarmauri_tool_jupyterruncell

3. Once installed, you can import and use the tool in your Python scripts or Jupyter notebooks.

If you prefer using Poetry, add the dependency to your pyproject.toml and install accordingly.

## Usage

Below is a simple example of how to utilize the JupyterRunCellTool in your Python code. This tool inherits from the Swarmauri base classes, ensuring it integrates into your existing Swarmauri-based projects.

Example of usage in a Python script or Jupyter notebook:

--------------------------------------------------------------------------------

from swarmauri_tool_jupyterruncell import JupyterRunCellTool

# Instantiate the tool
tool = JupyterRunCellTool()

# Simple code execution
result = tool(code="print('Hello from JupyterRunCellTool!')", timeout=5)

if result["success"]:
    print("Cell Output:", result["cell_output"])
    print("No errors captured.")
else:
    print("Cell Output:", result["cell_output"])
    print("Error Output:", result["error_output"])

--------------------------------------------------------------------------------

In this example:
• code: The Python code to run (as a string).  
• timeout: Optional parameter specifying the maximum number of seconds allowed for execution. Set to 0 or omit to disable timeouts.

The returned dictionary includes:
• cell_output: The captured stdout from the executed cell.  
• error_output: Any error messages or exceptions encountered.  
• success: A boolean indicating if execution was completed without unhandled exceptions.

## Additional Information

• The tool is designed to work within an active IPython session.  
• If no IPython session is detected, the tool will report an error.  
• Use the timeout feature to prevent indefinite execution of code blocks.  

## Dependencies

This package depends on:
• Python 3.10 or newer.  
• IPython for interactive cell execution.  
• swarmauri_core and swarmauri_base for Swarmauri integration.  

These dependencies are automatically installed when you install this package from PyPI, so no additional manual steps are required.  

---

Maintained by the Swarmauri team under the Apache-2.0 License.  
Please visit our PyPI page for the latest releases and updates.
