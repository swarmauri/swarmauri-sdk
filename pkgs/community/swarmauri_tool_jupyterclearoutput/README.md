
![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterclearoutput/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterclearoutput" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterclearoutput/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterclearoutput.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterclearoutput/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterclearoutput" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterclearoutput/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterclearoutput" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterclearoutput/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterclearoutput?label=swarmauri_tool_jupyterclearoutput&color=green" alt="PyPI - swarmauri_tool_jupyterclearoutput"/></a>
</p>

---

# Swarmauri Tool Jupyterclearoutput

JupyterClearOutputTool is a component designed for removing outputs from cells in a Jupyter Notebook. This ensures the notebook remains uncluttered, making it ideal for sharing and version control. It preserves the cell code and metadata, resets the execution counts, and logs the operation for auditing purposes, returning a cleaned notebook data structure.

## Installation

Install this package via PyPI:

    pip install swarmauri_tool_jupyterclearoutput

This package requires Python 3.10 or newer. By installing swarmauri_tool_jupyterclearoutput, all additional dependencies (such as nbconvert, swarmauri_core, and swarmauri_base) will be installed automatically.

## Usage

After installation, import and instantiate JupyterClearOutputTool to clear cell outputs from an in-memory notebook. You can load your notebook into a Python dictionary (for example, using json.load on a .ipynb file) and pass that dictionary to the tool.

Example usage:

--------------------------------------------------------------------------------
```python
from swarmauri_tool_jupyterclearoutput import JupyterClearOutputTool

# Suppose 'notebook_data' is a dictionary representing a Jupyter Notebook (e.g., loaded from a .ipynb file)
notebook_data = {
    "cells": [
        {
            "cell_type": "code",
            "execution_count": 1,
            "metadata": {},
            "outputs": [
                {"output_type": "stream", "name": "stdout", "text": ["Hello World\n"]}
            ],
            "source": ["print('Hello World')"]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["# This is a markdown cell"]
        }
    ],
    "metadata": {},
    "nbformat": 4,
    "nbformat_minor": 5
}

tool = JupyterClearOutputTool()
clean_notebook = tool(notebook_data)
```
# At this point, 'clean_notebook' contains the same notebook but with outputs cleared.

--------------------------------------------------------------------------------

You can then save the modified resulting dictionary back to a .ipynb file. This ensures the notebook is shared without potentially lengthy or sensitive outputs included.

## Dependencies

This package relies on:
• Python 3.10 or higher  
• swarmauri_core  
• swarmauri_base  
• nbconvert  

These dependencies are automatically managed by the package installer. No manual installation steps beyond "pip install swarmauri_tool_jupyterclearoutput" are required.

## Example Code Implementation

Below is the fully functional implementation for the core tool code:

--------------------------------------------------------------------------------
```python
"""
JupyterClearOutputTool.py

This module defines the JupyterClearOutputTool, a component that removes all outputs from a
Jupyter notebook while preserving cell code and metadata. It handles notebooks of varying
sizes and versions efficiently, logs the clear operation for auditing, and returns a clean
NotebookNode for further use.
"""

import logging
from typing import List, Dict, Any, Literal
from pydantic import Field
from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(ToolBase, "JupyterClearOutputTool")
class JupyterClearOutputTool(ToolBase):
    """
    JupyterClearOutputTool is a tool that removes the outputs from code cells in a Jupyter notebook.
    It preserves the cell code and metadata, ensures compatibility with various notebook versions,
    and returns a cleaned notebook data structure for further use.

    Attributes:
        version (str): The version of the JupyterClearOutputTool.
        parameters (List[Parameter]): A list of parameters required for clearing notebook outputs.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterClearOutputTool"]): The type identifier for this tool.
    """
    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="notebook_data",
                type="object",
                description="A dictionary that represents the Jupyter Notebook to clear outputs from.",
                required=True,
            ),
        ]
    )
    name: str = "JupyterClearOutputTool"
    description: str = "Removes outputs from a Jupyter notebook while preserving code and metadata."
    type: Literal["JupyterClearOutputTool"] = "JupyterClearOutputTool"

    def __call__(self, notebook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Removes all outputs from the provided Jupyter notebook data structure. Preserves
        cell code and metadata, and resets the execution counts. Logs the operation for auditing
        and returns the cleaned notebook.

        Args:
            notebook_data (Dict[str, Any]): A dictionary representing the Jupyter Notebook.

        Returns:
            Dict[str, Any]: The cleaned Jupyter Notebook dictionary with all cell outputs removed.

        Example:
            >>> tool = JupyterClearOutputTool()
            >>> clean_notebook = tool(notebook_data)
        """
        cells_cleared = 0

        # Iterate over all cells in the notebook and remove their outputs if they are code cells.
        for cell in notebook_data.get("cells", []):
            if cell.get("cell_type") == "code":
                if "outputs" in cell:
                    cell["outputs"] = []
                cell["execution_count"] = None
                cells_cleared += 1

        # Log the number of cells cleared for auditing.
        logger.info("Cleared outputs from %d cells in the notebook.", cells_cleared)

        # Return the cleaned notebook data structure.
        return notebook_data
```
--------------------------------------------------------------------------------

## License

This project is licensed under the Apache-2.0 License. For additional details, refer to the LICENSE file (if available).
