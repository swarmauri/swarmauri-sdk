
![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterreadnotebook/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterreadnotebook" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterreadnotebook/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterreadnotebook.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterreadnotebook/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterreadnotebook" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterreadnotebook/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterreadnotebook" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterreadnotebook/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterreadnotebook?label=swarmauri_tool_jupyterreadnotebook&color=green" alt="PyPI - swarmauri_tool_jupyterreadnotebook"/></a>
</p>

---

# Swarmauri Tool Jupyterreadnotebook

The swarmauri_tool_jupyterreadnotebook package provides a tool (`JupyterReadNotebookTool`) that reads a Jupyter Notebook file from the local filesystem, validates it using nbformat, and returns it for further processing. This is especially useful in scenarios where you need to programmatically read and inspect notebooks, or integrate them into automated workflows.

## Installation

1. Make sure you have Python 3.10 or above installed on your system.
2. Install the package using your preferred Python dependency management method. For example, with pip:
   • pip install swarmauri_tool_jupyterreadnotebook
   
   Alternatively, if you use Poetry, add the following to your pyproject.toml under dependencies, then run poetry install:
    ```toml
   [tool.poetry.dependencies]
   swarmauri_tool_jupyterreadnotebook = "*"
    ```
3. Ensure all required dependencies (found in pyproject.toml) are satisfied. This package relies on:
   • nbformat for reading and validating notebooks.
   • swarmauri_core and swarmauri_base for base tool definitions used throughout the Swarmauri ecosystem.

4. Once installed, you can immediately import and use the tool in your own project.

## Usage

The primary entry point is the JupyterReadNotebookTool class. It inherits from the Swarmauri base class ToolBase and integrates seamlessly into the Swarmauri environment. However, it can also be used independently.

Here is a simple usage example demonstrating how to invoke the tool in your code:

----------------------------------------------------------------------------------------------------
```python
from swarmauri_tool_jupyterreadnotebook import JupyterReadNotebookTool

def read_notebook_example():
    """
    Demonstrates how to read a Jupyter Notebook from the filesystem using the JupyterReadNotebookTool.
    """
    # Instantiate the tool
    notebook_reader = JupyterReadNotebookTool()

    # Provide the path to the notebook and optionally specify nbformat version
    result = notebook_reader(
        notebook_file_path="path_to_your_notebook.ipynb",
        as_version=4
    )

    if "notebook_node" in result:
        # Successfully read the notebook
        print("Notebook content:")
        notebook_data = result["notebook_node"]
        # You can inspect the notebook data as needed, e.g., listing cells
        for i, cell in enumerate(notebook_data.cells):
            print(f"Cell {i} type:", cell.cell_type)
    else:
        # An error occurred
        print("Error reading notebook:", result["error"])

read_notebook_example()
```
----------------------------------------------------------------------------------------------------

In this example:
• We instantiate JupyterReadNotebookTool with default settings.
• We call it, passing in the notebook file path and optional nbformat version.
• On a successful read, the dictionary returned will contain a "notebook_node" key with the parsed Jupyter notebook contents. Otherwise, it will contain an "error" key.

## Detailed Parameters for JupyterReadNotebookTool

• notebook_file_path (str): REQUIRED - The file path to the Jupyter Notebook to be read.
• as_version (int): OPTIONAL - The nbformat version (e.g., 4) to parse the notebook as. Defaults to 4 if not specified.

## Internal Logic

The tool follows these steps:

1. Reads the specified notebook file from the provided path.
2. Parses the notebook data using the requested nbformat version (default is version 4).
3. Validates notebook data to ensure schema compliance.
4. Returns the notebook data or an error message if something went wrong (such as a missing file or a validation error).

By leveraging this straightforward approach, the swarmauri_tool_jupyterreadnotebook package helps ensure that your notebooks remain valid, consistent, and ready for further processing.

---

## Dependencies

Below is a list of primary dependencies used by this package:
• nbformat for reading/executing/validating Jupyter Notebooks.
• swarmauri_core and swarmauri_base for base classes and decorators as required by Swarmauri components.
• pydantic for type validation (where relevant).

All dependencies are detailed in pyproject.toml. No additional manual installation is needed beyond installing this package.

---

## License

swarmauri_tool_jupyterreadnotebook is licensed under the Apache License 2.0. See the LICENSE file for more details.

---

© 2025 Swarmauri. All rights reserved.
