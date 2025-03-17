from typing import List, Literal, Dict, Any
import logging
import nbformat
from pydantic import Field
from nbformat.validator import NotebookValidationError

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase

"""
JupyterReadNotebookTool.py

This module defines the JupyterReadNotebookTool, a component that reads a Jupyter notebook file
from the filesystem, parses it into a NotebookNode object (using a specified nbformat version),

validates its integrity, and returns the resulting node for further processing. This component
inherits from the ToolBase class to seamlessly integrate with the system's tool architecture.
"""


@ComponentBase.register_type(ToolBase, "JupyterReadNotebookTool")
class JupyterReadNotebookTool(ToolBase):
    """
    JupyterReadNotebookTool is a tool that reads a Jupyter notebook file from the filesystem
    and returns a validated NotebookNode object. It supports specifying an nbformat version
    for parsing the file, logs the read operation, and handles both file and validation errors.

    Attributes:
        version (str): The version of the JupyterReadNotebookTool.
        parameters (List[Parameter]): A list of parameters required to read the notebook file.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterReadNotebookTool"]): The type identifier for the tool.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="notebook_file_path",
                input_type="string",
                description="The file path to the Jupyter notebook.",
                required=True,
            ),
            Parameter(
                name="as_version",
                input_type="integer",
                description="nbformat version to parse the notebook with (e.g., 4).",
                required=False,
            ),
        ]
    )
    name: str = "JupyterReadNotebookTool"
    description: str = (
        "Reads a Jupyter notebook file from the filesystem, parses it into a "
        "NotebookNode, validates its schema, and returns the node."
    )
    type: Literal["JupyterReadNotebookTool"] = "JupyterReadNotebookTool"

    def __call__(self, notebook_file_path: str, as_version: int = 4) -> Dict[str, Any]:
        """
        Reads a Jupyter notebook from the filesystem and returns it as a validated NotebookNode.

        Args:
            notebook_file_path (str): The file path to the Jupyter notebook.
            as_version (int, optional): The nbformat version to parse the file as. Defaults to 4.

        Returns:
            Dict[str, Any]: A dictionary containing either the NotebookNode object under the
                            "notebook_node" key or an "error" key with a message if an error
                            occurred.
        """
        logger = logging.getLogger(__name__)
        logger.info(
            "Attempting to read Jupyter notebook from '%s' with nbformat version '%d'.",
            notebook_file_path,
            as_version,
        )

        try:
            # Read and parse the notebook
            nb_data = nbformat.read(notebook_file_path, as_version=as_version)
            # Validate the notebook's schema
            nbformat.validate(nb_data)
            logger.info(
                "Successfully read and validated notebook from '%s'.",
                notebook_file_path,
            )
            return {"notebook_node": nb_data}
        except FileNotFoundError:
            error_message = f"File not found: {notebook_file_path}"
            logger.error(error_message)
            return {"error": error_message}
        except NotebookValidationError as e:
            error_message = f"Notebook validation error: {str(e)}"
            logger.error(error_message)
            return {"error": error_message}
        except Exception as e:
            error_message = f"Failed to read notebook: {str(e)}"
            logger.error(error_message)
            return {"error": error_message}
