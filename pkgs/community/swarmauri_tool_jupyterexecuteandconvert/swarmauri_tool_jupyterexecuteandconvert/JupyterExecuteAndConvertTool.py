"""
JupyterExecuteAndConvertTool.py

This module defines the JupyterExecuteAndConvertTool, a component that executes a Jupyter
notebook file and converts it to a specified format (e.g., HTML or PDF) using nbconvert.
It leverages the ToolBase and ComponentBase classes from the swarmauri framework to integrate
seamlessly with the system's tool architecture.

The JupyterExecuteAndConvertTool can handle timeouts, log the execution process, and return
information about the converted file. Errors are handled gracefully and surfaced back to
the caller as needed.
"""

import os
import logging
import subprocess
from typing import List, Dict, Any, Literal
from pydantic import Field

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(ToolBase, "JupyterExecuteAndConvertTool")
class JupyterExecuteAndConvertTool(ToolBase):
    """
    JupyterExecuteAndConvertTool is a tool that executes a Jupyter notebook file via the
    nbconvert CLI and then converts the executed notebook to a specified output format.
    It handles timeouts, logs the process, and provides a return value that contains
    the path to the converted file and the status of the operation.

    Attributes:
        version (str): The version of the JupyterExecuteAndConvertTool.
        parameters (List[Parameter]): A list of parameters required to perform the
            notebook execution and conversion.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterExecuteAndConvertTool"]): The type identifier for the tool.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="notebook_path",
                input_type="string",
                description="Path of the Jupyter notebook file to execute.",
                required=True,
            ),
            Parameter(
                name="output_format",
                input_type="string",
                description="The format to which the executed notebook should be converted (e.g., 'html', 'pdf').",
                required=True,
                enum=["html", "pdf"],
            ),
            Parameter(
                name="execution_timeout",
                input_type="number",
                description="Timeout (in seconds) for notebook execution.",
                required=False,
            ),
        ]
    )
    name: str = "JupyterExecuteAndConvertTool"
    description: str = (
        "Executes a Jupyter notebook and converts it to a specified format."
    )
    type: Literal["JupyterExecuteAndConvertTool"] = "JupyterExecuteAndConvertTool"

    def __call__(
        self,
        notebook_path: str,
        output_format: str = "html",
        execution_timeout: int = 600,
    ) -> Dict[str, Any]:
        """
        Executes the specified Jupyter notebook file and converts it to the chosen output format.

        Args:
            notebook_path (str): The path to the Jupyter notebook to execute.
            output_format (str): The format for the output conversion. Defaults to "html".
            execution_timeout (int): The maximum time (in seconds) allowed for execution.
                                     Defaults to 600 (10 minutes).

        Returns:
            Dict[str, Any]: A dictionary containing the conversion status and path to the
            output file. In case of an error, the dictionary keys "error" and "message"
            will be set to describe the problem.

        Example:
            >>> tool = JupyterExecuteAndConvertTool()
            >>> result = tool(
            ...     notebook_path="example_notebook.ipynb",
            ...     output_format="pdf",
            ...     execution_timeout=300
            ... )
            >>> print(result)
            {
                "converted_file": "example_notebook.pdf",
                "status": "success"
            }
        """
        try:
            logger.info("Starting Jupyter notebook execution process.")
            if not os.path.exists(notebook_path):
                logger.error(f"Notebook not found: {notebook_path}")
                return {
                    "error": "Notebook file does not exist.",
                    "message": notebook_path,
                }

            # Derive base name and set output notebook name
            base_name = os.path.splitext(os.path.basename(notebook_path))[0]
            executed_notebook = f"executed_{base_name}.ipynb"

            # Execute the notebook via CLI with nbconvert
            execute_cmd = [
                "jupyter",
                "nbconvert",
                "--to",
                "notebook",
                "--execute",
                notebook_path,
                "--output",
                executed_notebook,
            ]

            logger.info(f"Executing notebook via command: {' '.join(execute_cmd)}")
            subprocess.run(execute_cmd, check=True, timeout=execution_timeout)
            logger.info(f"Notebook execution completed: {executed_notebook}")

        except subprocess.TimeoutExpired:
            logger.error(
                f"Notebook execution timed out after {execution_timeout} seconds."
            )
            return {
                "error": "TimeoutExpired",
                "message": f"Notebook execution timed out after {execution_timeout} seconds.",
            }
        except subprocess.CalledProcessError as cpe:
            logger.error(f"Error occurred during notebook execution: {str(cpe)}")
            return {
                "error": "ExecutionError",
                "message": f"An error occurred while executing the notebook: {str(cpe)}",
            }
        except Exception as e:
            logger.error(f"Unexpected error during execution: {str(e)}")
            return {
                "error": "UnexpectedError",
                "message": f"An unexpected error occurred: {str(e)}",
            }

        try:
            logger.info("Starting notebook conversion process.")
            # Determine the conversion command
            convert_cmd = [
                "jupyter",
                "nbconvert",
                "--to",
                output_format,
                executed_notebook,
            ]
            logger.info(f"Converting notebook via command: {' '.join(convert_cmd)}")
            subprocess.run(convert_cmd, check=True)

            # Determine the name of the converted file
            converted_file = f"{os.path.splitext(executed_notebook)[0]}.{output_format}"
            logger.info(
                f"Notebook successfully converted to {output_format}. File: {converted_file}"
            )

            return {"converted_file": converted_file, "status": "success"}

        except subprocess.CalledProcessError as cpe:
            logger.error(f"Error occurred during notebook conversion: {str(cpe)}")
            return {
                "error": "ConversionError",
                "message": f"An error occurred while converting the notebook: {str(cpe)}",
            }
        except Exception as e:
            logger.error(f"Unexpected error during conversion: {str(e)}")
            return {
                "error": "UnexpectedError",
                "message": f"An unexpected error occurred: {str(e)}",
            }
