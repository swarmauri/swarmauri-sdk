"""
JupyterExportPythonTool.py

This module defines the JupyterExportPythonTool, a component that exports a Jupyter Notebook
(NotebookNode) to a Python script. It leverages the swarmauri tool architecture and nbconvert
to perform the notebook-to-script conversion, supports optional custom templates, and logs
errors as needed.
"""

import logging
from typing import List, Optional, Dict, Any, Literal

from pydantic import Field
from nbformat import NotebookNode
from nbconvert import PythonExporter

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(ToolBase, "JupyterExportPythonTool")
class JupyterExportPythonTool(ToolBase):
    """
    JupyterExportPythonTool is a tool that converts a Jupyter Notebook (NotebookNode) into
    a Python script. It supports custom templates for export, logs operations and errors,
    and returns the exported Python script as a string.

    Attributes:
        version (str): The version of the JupyterExportPythonTool.
        parameters (List[Parameter]): A list of parameters required to perform the export.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterExportPythonTool"]): The type identifier for the tool.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="notebook",
                input_type="object",
                description="The NotebookNode object representing the Jupyter Notebook to export.",
                required=True,
            ),
            Parameter(
                name="template_file",
                input_type="string",
                description="Optional custom template path for exporting the notebook to a Python script.",
                required=False,
            ),
        ]
    )
    name: str = "JupyterExportPythonTool"
    description: str = "Converts Jupyter Notebooks to Python scripts."
    type: Literal["JupyterExportPythonTool"] = "JupyterExportPythonTool"

    def __call__(
        self, notebook: NotebookNode, template_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Converts the provided Jupyter Notebook (NotebookNode) to a Python script using
        nbconvert. Optionally applies a custom template if template_file is provided.

        Args:
            notebook (NotebookNode): The notebook object to be exported.
            template_file (str, optional): Path to a custom template file to structure
                                           the exported Python script.

        Returns:
            Dict[str, Any]: A dictionary containing either "exported_script" with the
                            Python code as a string, or an "error" message if an exception
                            occurred during export.

        Example:
            >>> tool = JupyterExportPythonTool()
            >>> nb_node = some_function_returning_notebook_node()
            >>> export_result = tool(nb_node, template_file='my_template.tpl')
            >>> if 'exported_script' in export_result:
            ...     print("Export Successful!")
            ... else:
            ...     print(export_result['error'])
        """
        try:
            logger.info("Starting notebook export to Python script.")
            python_exporter = PythonExporter()

            if template_file:
                logger.debug(f"Using custom template file: {template_file}")
                python_exporter.template_file = template_file

            exported_script, _ = python_exporter.from_notebook_node(notebook)
            logger.info("Notebook export completed successfully.")

            return {"exported_script": exported_script}
        except Exception as e:
            logger.error(f"Notebook export failed: {str(e)}")
            return {"error": f"Export failed: {str(e)}"}
