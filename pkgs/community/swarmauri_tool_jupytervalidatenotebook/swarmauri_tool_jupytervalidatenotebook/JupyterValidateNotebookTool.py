"""
JupyterValidateNotebookTool.py

This module defines the JupyterValidateNotebookTool, a component that validates a Jupyter
notebook against its JSON schema using nbformat. It inherits from the swarmauri framework
classes to integrate seamlessly as a tool that can be invoked with a NotebookNode as input.
"""

import logging
from typing import List, Dict
from pydantic import Field
from typing_extensions import Literal
import jsonschema
import nbformat
from nbformat import NotebookNode
from nbformat.validator import NotebookValidationError

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase


@ComponentBase.register_type(ToolBase, "JupyterValidateNotebookTool")
class JupyterValidateNotebookTool(ToolBase):
    """
    JupyterValidateNotebookTool is a tool that validates a Jupyter NotebookNode against
    its JSON schema. It leverages nbformat to perform the validation, logs any discrepancies
    or errors, and returns a report along with a boolean indicating validity.

    Attributes:
        version (str): The version of the JupyterValidateNotebookTool.
        parameters (List[Parameter]): A list of parameters needed for notebook validation.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterValidateNotebookTool"]): The type identifier for the tool.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="notebook",
                input_type="object",
                description="A Jupyter NotebookNode object to validate.",
                required=True,
            ),
        ]
    )
    name: str = "JupyterValidateNotebookTool"
    description: str = "Validates a Jupyter notebook structure against its JSON schema."
    type: Literal["JupyterValidateNotebookTool"] = "JupyterValidateNotebookTool"

    def __call__(self, notebook: NotebookNode) -> Dict[str, str]:
        logger = logging.getLogger(__name__)
        try:
            # Explicitly check that the notebook is version 4.
            if notebook.get("nbformat") != 4:
                raise NotebookValidationError(
                    f"Invalid nbformat version: {notebook.get('nbformat')}. Expected 4."
                )
            nbformat.validate(notebook)
            logger.info("Notebook validation succeeded.")
            return {
                "valid": "True",
                "report": "The notebook is valid according to its JSON schema.",
            }
        except (
            NotebookValidationError,
            jsonschema.ValidationError,
            AttributeError,
        ) as e:
            logger.error(f"Notebook validation error: {e}")
            return {"valid": "False", "report": f"Validation error: {str(e)}"}
        except Exception as e:
            logger.error(f"An unexpected error occurred during validation: {e}")
            return {"valid": "False", "report": f"Unexpected error: {str(e)}"}
