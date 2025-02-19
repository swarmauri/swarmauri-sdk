"""
JupyterExecuteCellTool.py

This module defines the JupyterExecuteCellTool, a component that sends code cells to the
Jupyter kernel for execution, captures their output, and returns the results. It leverages
the ToolBase and ComponentBase classes from the swarmauri framework to integrate seamlessly
with the system's tool architecture.

The JupyterExecuteCellTool supports synchronous code execution with a configurable timeout
interval. The tool logs and gracefully handles execution failures, returning any errors
captured during execution.
"""

import concurrent.futures
import logging
import io
import traceback
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, List, Literal, Optional

from IPython import get_ipython
from pydantic import Field

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(ToolBase, "JupyterExecuteCellTool")
class JupyterExecuteCellTool(ToolBase):
    """
    JupyterExecuteCellTool is a tool that sends code to a Jupyter kernel for execution,
    capturing stdout, stderr, and any exceptions encountered. It supports a configurable
    timeout to prevent long-running code from blocking execution indefinitely.

    Attributes:
        version (str): The version of the JupyterExecuteCellTool.
        parameters (List[Parameter]): A list of parameters required to execute a notebook cell.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterExecuteCellTool"]): The type identifier for the tool.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="code",
                type="string",
                description="The code to be executed in the Jupyter kernel.",
                required=True,
            ),
            Parameter(
                name="timeout",
                type="number",
                description="Timeout in seconds for the cell execution.",
                required=False,
                default=30,
            ),
        ]
    )
    name: str = "JupyterExecuteCellTool"
    description: str = "Executes code cells within a Jupyter kernel environment."
    type: Literal["JupyterExecuteCellTool"] = "JupyterExecuteCellTool"

    def __call__(self, code: str, timeout: Optional[int] = 30) -> Dict[str, str]:
        """
        Executes the provided code cell in a Jupyter kernel with a specified timeout.

        Args:
            code (str): The code cell content to execute.
            timeout (Optional[int]): The maximum number of seconds to allow for code execution.
                                     Defaults to 30 seconds.

        Returns:
            Dict[str, str]: A dictionary containing the execution results. Keys include:
                - 'stdout': The standard output captured from the execution.
                - 'stderr': The error output captured from the execution, if any.
                - 'error':  Any exception or error message if the execution fails or times out.

        Example:
            >>> executor = JupyterExecuteCellTool()
            >>> result = executor("print('Hello, world!')")
            >>> print(result['stdout'])  # Should contain "Hello, world!"
        """

        def _run_code(cell_code: str) -> Dict[str, str]:
            """
            Internal helper function to run the provided code in the current IPython kernel,
            capturing stdout and stderr.
            """
            ip = get_ipython()
            if not ip:
                logger.error("No active IPython kernel found.")
                return {
                    "stdout": "",
                    "stderr": "No active IPython kernel found.",
                    "error": "KernelNotFoundError",
                }

            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()

            try:
                with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                    # Execute the cell in IPython with store_history=True so that it behaves
                    # like a normal code cell in a notebook environment.
                    ip.run_cell(cell_code, store_history=True)
            except Exception as exc:
                logger.error("An exception occurred while executing the cell: %s", exc)
                return {
                    "stdout": stdout_buffer.getvalue(),
                    "stderr": stderr_buffer.getvalue(),
                    "error": str(traceback.format_exc()),
                }

            return {
                "stdout": stdout_buffer.getvalue(),
                "stderr": stderr_buffer.getvalue(),
                "error": "",
            }

        # Use a ThreadPoolExecutor to support timeouts during synchronous execution.
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_run_code, code)
            try:
                result = future.result(timeout=timeout)
                logger.info("Cell executed successfully.")
                return result
            except concurrent.futures.TimeoutError:
                logger.error("Cell execution exceeded timeout of %s seconds.", timeout)
                return {
                    "stdout": "",
                    "stderr": "",
                    "error": f"Execution timed out after {timeout} seconds.",
                }
            except Exception as exc:
                logger.error("Unexpected error during cell execution: %s", exc)
                return {
                    "stdout": "",
                    "stderr": "",
                    "error": f"An unexpected error occurred: {str(exc)}",
                }
