"""
JupyterFromDictTool.py

This module defines the JupyterFromDictTool, a component that takes a dictionary representing
a Jupyter notebook structure and converts it into a validated NotebookNode. It provides logging
throughout the conversion process and gracefully handles errors.
"""

import logging
from typing import List, Dict, Union, Literal
from pydantic import Field
from nbformat import from_dict, validate, NotebookNode, ValidationError

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(ToolBase, "JupyterFromDictTool")
class JupyterFromDictTool(ToolBase):
    """
    JupyterFromDictTool is a tool that converts a dictionary representing a Jupyter notebook
    into a validated NotebookNode object. It inherits from ToolBase and integrates with the
    swarmauri framework, allowing the conversion process to be easily reused within the system.

    Attributes:
        version (str): The version of the JupyterFromDictTool.
        parameters (List[Parameter]): A list of parameters required for tool invocation.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterFromDictTool"]): The type identifier for the tool.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="notebook_dict",
                input_type="object",
                description="The dictionary representing the notebook structure.",
                required=True,
            )
        ]
    )
    name: str = "JupyterFromDictTool"
    description: str = "Converts a dictionary into a validated Jupyter NotebookNode."
    type: Literal["JupyterFromDictTool"] = "JupyterFromDictTool"

    def __call__(self, notebook_dict: Dict) -> Dict[str, Union[str, NotebookNode]]:
        """
        Converts the provided dictionary into a NotebookNode, validates it against the nbformat
        schema, and returns the resulting NotebookNode in a dictionary response.

        Args:
            notebook_dict (Dict): The dictionary containing notebook structure.

        Returns:
            Dict[str, Union[str, NotebookNode]]: A dictionary containing either the validated
            NotebookNode or an error message indicating what went wrong during the conversion.

        Example:
            >>> jupyter_tool = JupyterFromDictTool()
            >>> notebook_example = {
            ...     "nbformat": 4,
            ...     "nbformat_minor": 5,
            ...     "cells": [],
            ...     "metadata": {}
            ... }
            >>> result = jupyter_tool(notebook_example)
            {
              'notebook_node': NotebookNode(nbformat=4, nbformat_minor=5, cells=[], metadata={})
            }
        """
        try:
            logger.info("Starting conversion from dictionary to NotebookNode.")
            notebook_node: NotebookNode = from_dict(notebook_dict)
            logger.info("NotebookNode created. Validating NotebookNode.")
            validate(notebook_node)
            logger.info("NotebookNode validation successful.")
            return {"notebook_node": notebook_node}
        except ValidationError as ve:
            logger.error(f"NotebookNode validation error: {ve}")
            return {"error": f"NotebookNode validation error: {str(ve)}"}
        except Exception as e:
            logger.error(f"Failed to convert dictionary to NotebookNode: {e}")
            return {"error": f"An error occurred: {str(e)}"}
