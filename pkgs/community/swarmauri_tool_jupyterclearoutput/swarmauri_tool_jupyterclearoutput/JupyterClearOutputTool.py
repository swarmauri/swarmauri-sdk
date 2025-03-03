"""
JupyterClearOutputTool.py

This module defines the JupyterClearOutputTool, a component that removes all outputs from a
Jupyter notebook while preserving cell code and metadata. It handles notebooks of varying
sizes and versions efficiently, logs the clear operation for auditing, and returns a clean
NotebookNode for further use.
"""

import logging
from typing import Any, Dict, List, Literal

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase

from swarmauri_standard.tools.Parameter import Parameter

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
                input_type="object",
                description="A dictionary that represents the Jupyter Notebook to clear outputs from.",
                required=True,
            ),
        ]
    )
    name: str = "JupyterClearOutputTool"
    description: str = (
        "Removes outputs from a Jupyter notebook while preserving code and metadata."
    )
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
