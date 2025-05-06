"""
JupyterExportMarkdownTool.py

This module defines the JupyterExportMarkdownTool, a component that converts a Jupyter
Notebook into Markdown format. It demonstrates how to inherit from the ToolBase class
and integrate with the swarmauri framework. The tool supports custom templates, styling,
and logs export operations to help track usage and potential errors.
"""

import logging
from typing import List, Literal, Dict, Optional, Any
from pydantic import Field

import nbformat
from nbconvert import MarkdownExporter

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(ToolBase, "JupyterExportMarkdownTool")
class JupyterExportMarkdownTool(ToolBase):
    """
    JupyterExportMarkdownTool converts a Jupyter Notebook (represented as a NotebookNode or JSON-like
    structure) into Markdown format. It supports a custom template for formatting and allows optional
    styling resources. This tool is designed for effortless integration with static site generators.

    Attributes:
        version (str): The version of the JupyterExportMarkdownTool.
        parameters (List[Parameter]): A list of parameters for notebook export.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterExportMarkdownTool"]): The type identifier for the tool.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="notebook_json",
                input_type="object",
                description=(
                    "A JSON-like dictionary representing the Jupyter Notebook to export. "
                    "It should conform to the NotebookNode structure."
                ),
                required=True,
            ),
            Parameter(
                name="template",
                input_type="string",
                description=(
                    "An optional nbconvert-compatible template name or path to "
                    "customize the Markdown output."
                ),
                required=False,
            ),
            Parameter(
                name="styles",
                input_type="string",
                description=(
                    "Optional custom CSS style definitions as a string. "
                    "These styles will be embedded into the exported Markdown."
                ),
                required=False,
            ),
        ]
    )
    name: str = "JupyterExportMarkdownTool"
    description: str = "Converts a Jupyter Notebook into Markdown format."
    type: Literal["JupyterExportMarkdownTool"] = "JupyterExportMarkdownTool"

    def __call__(
        self,
        notebook_json: Dict[str, Any],
        template: Optional[str] = None,
        styles: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Converts the provided Jupyter Notebook JSON into Markdown format using nbconvert.

        Args:
            notebook_json (Dict[str, Any]): A dictionary representing the Jupyter notebook
                structure (NotebookNode). Must follow nbformat specifications.
            template (Optional[str]): An optional template name or path for customizing the
                Markdown output.
            styles (Optional[str]): A string of custom CSS rules to embed in the exported
                Markdown. Useful for styling code blocks, headings, etc.

        Returns:
            Dict[str, str]: A dictionary containing either the exported Markdown content or
            an error message if the conversion fails.

         Example:
            >>> tool = JupyterExportMarkdownTool()
            >>> notebook_dict = {
            ...     "cells": [
            ...         {
            ...             "cell_type": "markdown",
            ...             "metadata": {},
            ...             "source": ["# Sample Notebook\\n", "Some introductory text."]
            ...         }
            ...     ],
            ...     "metadata": {},
            ...     "nbformat": 4,
            ...     "nbformat_minor": 5
            ... }
            >>> result = tool(notebook_dict)
            >>> print(result["exported_markdown"])
            # Sample Notebook
            Some introductory text.
        """

        logger.info("Starting export of notebook to Markdown.")

        try:
            # Convert the incoming JSON to a NotebookNode
            nb_node = nbformat.from_dict(notebook_json)
            logger.info("Notebook JSON successfully parsed into a NotebookNode.")

            # Convert each cell's source to a string if it is a list
            for cell in nb_node.cells:
                if isinstance(cell.get("source", ""), list):
                    cell["source"] = "".join(cell["source"])

            # Create an nbconvert MarkdownExporter
            exporter = MarkdownExporter()

            # If a template is provided, apply it
            if template:
                exporter.template_file = template
                logger.info(f"Using custom template: {template}")

            # Prepare resources (e.g., for styling)
            resources = {}
            if styles:
                # The CSS styles are stored in a list (nbconvert expects CSS as a list of strings)
                resources["inlining"] = {"css": [styles]}
                logger.info("Custom CSS styles have been applied.")

            # Perform the conversion
            markdown_content, _ = exporter.from_notebook_node(
                nb_node, resources=resources
            )
            logger.info("Notebook successfully exported to Markdown.")

            return {
                "tool": "JupyterExportMarkdownTool",
                "exported_markdown": markdown_content,
            }

        except Exception as e:
            error_message = f"Failed to export notebook to Markdown: {str(e)}"
            logger.error(error_message, exc_info=True)
            return {"error": error_message}
