"""
JupyterRunCellTool.py

This module defines the JupyterRunCellTool, a component that executes Python
code cells
in an interactive IPython environment. It captures the standard output and
standard error
streams, handles timeouts, and returns the results for further processing. The
tool
integrates seamlessly with the swarmauri tool architecture and supports
automated
testing workflows.
"""

import concurrent.futures
import contextlib
import io
import logging
import traceback
from typing import List, Literal, Optional, Dict, Any
from pydantic import Field

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@ComponentBase.register_type(ToolBase, "JupyterRunCellTool")
class JupyterRunCellTool(ToolBase):
    """
    JupyterRunCellTool is a tool that executes Python code within an
    interactive IPython shell.
    It captures the stdout and stderr streams, handles execution timeouts, logs
    the process,
    and returns the output for further processing.

    Attributes:
        version (str): The version of the JupyterRunCellTool.
        parameters (List[Parameter]): A list of parameters that define the code
        snippet to be run
                                      and the optional timeout in seconds.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterRunCellTool"]): The type identifier for the tool.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="code",
                input_type="string",
                description="The Python code to run in the IPython cell.",
                required=True,
            ),
            Parameter(
                name="timeout",
                input_type="number",
                description=(
                    "Optional timeout (in seconds) for the code execution. "
                    "Default is 0 (no timeout)."
                ),
                required=False,
                default=0,
            ),
        ]
    )
    name: str = "JupyterRunCellTool"
    description: str = (
        "Executes Python code in an IPython environment, capturing "
        "stdout and stderr."
    )
    type: Literal["JupyterRunCellTool"] = "JupyterRunCellTool"

    def __call__(
        self, code: str, timeout: Optional[float] = 0
    ) -> Dict[str, Any]:
        """
        Executes the provided Python code in an interactive IPython session.

        Args:
            code (str): The Python code to execute in a cell.
            timeout (float, optional): The maximum amount of time (in seconds)
            to allow for
                                       code execution. If 0 or not provided, no
                                       timeout
                                       is imposed. Defaults to 0.

        Returns:
            Dict[str, Any]: A dictionary containing:
                - "cell_output" (str): Captured standard output from running
                  the code cell.
                - "error_output" (str): Captured errors or exception traces, if
                  any.
                - "success" (bool): Indicates if execution succeeded without
                  any unhandled exceptions.

        Example:
            >>> tool = JupyterRunCellTool()
            >>> result = tool(\"\"\"print('Hello, world!')\"\"\")
            >>> print(result)
            {
                'cell_output': 'Hello, world!\\n',
                'error_output': '',
                'success': True
            }
        """
        from IPython import get_ipython

        logger.info("JupyterRunCellTool called with code:\n%s", code)
        logger.info("Timeout set to %s seconds.", timeout)

        # Retrieve the current IPython shell instance
        shell = get_ipython()
        if shell is None:
            logger.error("No active IPython shell found.")
            return {
                "cell_output": "",
                "error_output": "Error: No active IPython shell available.",
                "success": False,
            }

        def _run_cell() -> Dict[str, Any]:
            output_buffer = io.StringIO()
            error_buffer = io.StringIO()

            try:
                with (
                    contextlib.redirect_stdout(output_buffer),
                    contextlib.redirect_stderr(error_buffer),
                ):
                    shell.run_cell(code)
                cell_output = output_buffer.getvalue()
                error_output = error_buffer.getvalue()
                logger.info("Cell execution completed.")
                logger.debug("Captured stdout: %s", cell_output.strip())
                logger.debug("Captured stderr: %s", error_output.strip())
                return {
                    "cell_output": cell_output,
                    "error_output": error_output,
                    "success": True,
                }
            except Exception as exc:
                logger.error(
                    "An error occurred during cell execution: %s", str(exc)
                )
                traceback_str = traceback.format_exc()
                cell_output = output_buffer.getvalue()
                error_output = error_buffer.getvalue() + "\n" + traceback_str
                return {
                    "cell_output": cell_output,
                    "error_output": error_output,
                    "success": False,
                }

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_run_cell)
            try:
                if timeout and timeout > 0:
                    return future.result(timeout=timeout)
                return future.result()
            except concurrent.futures.TimeoutError:
                logger.error("TimeoutError: Cell execution timed out.")
                return {
                    "cell_output": "",
                    "error_output": "TimeoutError: Cell execution timed out.",
                    "success": False,
                }
