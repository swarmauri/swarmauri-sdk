
<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutenotebook/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterexecutenotebook" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecutenotebook/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecutenotebook.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutenotebook/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterexecutenotebook" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutenotebook/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterexecutenotebook" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutenotebook/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexecutenotebook?label=swarmauri_tool_jupyterexecutenotebook&color=green" alt="PyPI - swarmauri_tool_jupyterexecutenotebook"/></a>
</p>

---

# Swarmauri Tool Jupyter Execute Notebook

The swarmauri_tool_jupyterexecutenotebook package provides a tool for executing all cells in a Jupyter notebook in sequence, capturing outputs and returning the fully updated NotebookNode object. It leverages the Swarmauri framework's base and core components.

## Installation

To install swarmauri_tool_jupyterexecutenotebook, make sure you have Python 3.10 or later:

1. Using pip:
   • (Recommended) Create and activate a virtual environment.  
   • Run:  
     pip install swarmauri_tool_jupyterexecutenotebook

2. Using Poetry in an existing project:
   • poetry add swarmauri_tool_jupyterexecutenotebook

This will automatically install all dependencies required to run the JupyterExecuteNotebookTool.

## Usage

The principal component of this package is the JupyterExecuteNotebookTool, which executes a given notebook, capturing cell outputs and errors. Below is a quick reference for using the tool programmatically in your Python code.

Example usage:

---------------------------------------------------------------------------------
from swarmauri_tool_jupyterexecutenotebook import JupyterExecuteNotebookTool

def execute_my_notebook():
    """
    Demonstrates how to instantiate and use the JupyterExecuteNotebookTool to
    execute a Jupyter notebook file. This includes capturing outputs and
    error messages.
    """
    # Create an instance of the tool
    tool = JupyterExecuteNotebookTool()

    # Execute the Jupyter notebook; specify the path to your notebook
    executed_notebook = tool(
        notebook_path="my_notebook.ipynb",
        timeout=60  # Optional: defaults to 30 if not provided
    )

    # The returned `executed_notebook` is a NotebookNode with outputs captured
    return executed_notebook

if __name__ == "__main__":
    result_notebook = execute_my_notebook()
    # You can further analyze 'result_notebook' outputs here
---------------------------------------------------------------------------------

In this example:
• The notebook_path parameter is a required string referencing the target notebook file.  
• The optional timeout parameter defines how long each cell can take to run before throwing an error (default is 30 seconds).  

The executed NotebookNode object will contain both new outputs and any error messages generated during execution.

## Dependencies

This package relies on:
• swarmauri_core for base components.  
• swarmauri_base for the ToolBase class.  
• nbconvert, nbformat, and nbclient for handling and executing Jupyter notebooks.  

When you install swarmauri_tool_jupyterexecutenotebook via pip or Poetry, these dependencies are automatically handled for you. Refer to the project's pyproject.toml for the full list of dependencies and version requirements.

---

This README is provided as part of the swarmauri_tool_jupyterexecutenotebook package. If you have any questions or issues, please consult our documentation or open a support request. Thank you for using Swarmauri!
