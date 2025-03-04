"""
JupyterWriteNotebookTool.py

This module defines the JupyterWriteNotebookTool, a component that converts a Jupyter notebook
structure (NotebookNode) to JSON format and writes the data to a specified file. It inherits
from the ToolBase class of the swarmauri framework, providing a fully-featured implementation
for writing notebook content to disk.

The tool validates notebook data, handles potential I/O operations, logs its actions, and
confirms the success of write operations to ensure notebook integrity.
"""

import json
import logging
from typing import List, Literal, Dict
from pydantic import Field
from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(ToolBase, "JupyterWriteNotebookTool")
class JupyterWriteNotebookTool(ToolBase):
    """
    JupyterWriteNotebookTool is responsible for converting a Jupyter NotebookNode
    structure into JSON and writing it to disk. It ensures the notebook format
    remains valid, including optional read-back verification to confirm the file's
    integrity.

    Attributes:
        version (str): The version of the JupyterWriteNotebookTool.
        parameters (List[Parameter]): A list of parameters required to perform the write operation.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterWriteNotebookTool"]): The type identifier for the tool.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="notebook_data",
                input_type="object",
                description="The notebook content as a dictionary/NotebookNode structure.",
                required=True,
            ),
            Parameter(
                name="output_file",
                input_type="string",
                description="Path to the output file where the notebook JSON will be written.",
                required=True,
            ),
            Parameter(
                name="encoding",
                input_type="string",
                description="File encoding to use when writing the notebook JSON.",
                required=False,
                default="utf-8",
            ),
        ]
    )
    name: str = "JupyterWriteNotebookTool"
    description: str = "Writes a Jupyter NotebookNode to a file in JSON format."
    type: Literal["JupyterWriteNotebookTool"] = "JupyterWriteNotebookTool"

    def __call__(
        self, notebook_data: dict, output_file: str, encoding: str = "utf-8"
    ) -> Dict[str, str]:
        """
        Writes the provided Jupyter notebook data (NotebookNode) to the specified
        output file in JSON format. The method uses the selected encoding and
        handles potential I/O exceptions.

        Args:
            notebook_data (dict): The Jupyter NotebookNode structure represented as a dictionary.
            output_file (str): The path to the file where the notebook JSON will be written.
            encoding (str, optional): The file encoding to use. Defaults to "utf-8".

        Returns:
            Dict[str, str]: A dictionary indicating the success of the operation or an error message.
                            For example:
                            {
                                "message": "Notebook written successfully",
                                "file_path": "path/to/notebook.ipynb"
                            }

                            Or in case of an error:
                            {
                                "error": "An error occurred: <error message>"
                            }
        """
        logger.info(
            "Attempting to write notebook to file '%s' with encoding '%s'",
            output_file,
            encoding,
        )

        try:
            # Convert the notebook data to JSON text.
            json_data = json.dumps(notebook_data, ensure_ascii=False, indent=2)

            # Write the JSON data to file.
            with open(output_file, "w", encoding=encoding) as f:
                f.write(json_data)
            logger.info("Notebook successfully written to '%s'", output_file)

            # Optional read-back check to confirm integrity.
            with open(output_file, "r", encoding=encoding) as f:
                content = json.load(f)
            if not content:
                logger.error("Notebook data verification failed: File is empty.")
                return {
                    "error": f"Notebook data verification failed: File '{output_file}' is empty."
                }

            logger.info("Notebook data verification successful for '%s'", output_file)
            return {
                "message": "Notebook written successfully",
                "file_path": output_file,
            }

        except Exception as e:
            error_msg = f"An error occurred during notebook write operation: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
