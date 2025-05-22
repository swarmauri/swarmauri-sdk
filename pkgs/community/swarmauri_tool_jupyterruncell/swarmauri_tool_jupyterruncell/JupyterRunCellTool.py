"""JupyterRunCellTool.py

Execute Python code on a remote Jupyter server via its REST API.

The tool sends code to a running kernel using HTTP requests and returns the
captured stdout and stderr. It integrates with the Swarmauri tool architecture
to allow automated execution of notebook cells in external Jupyter services.
"""

import logging
import traceback
from typing import List, Literal, Optional, Dict, Any

import httpx

from httpx import HTTPError
from pydantic import Field

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase

# Configure a logger for this module.
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@ComponentBase.register_type(ToolBase, "JupyterRunCellTool")
class JupyterRunCellTool(ToolBase):
    """
    JupyterRunCellTool executes Python code using a Jupyter server's REST API.
    It sends a request to a running kernel, captures stdout and stderr from the
    response, and returns the results for further processing.

    Attributes:
        version (str): The version of the JupyterRunCellTool.
        parameters (List[Parameter]): A list of parameters that define the code snippet to be run
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
                description="The Python code to run on the Jupyter server.",
                required=True,
            ),
            Parameter(
                name="base_url",
                input_type="string",
                description="Base URL of the Jupyter server REST API.",
                required=True,
            ),
            Parameter(
                name="kernel_id",
                input_type="string",
                description="Identifier of the kernel used for execution.",
                required=True,
            ),
            Parameter(
                name="token",
                input_type="string",
                description="Authentication token for the Jupyter server.",
                required=False,
                default=None,
            ),
            Parameter(
                name="timeout",
                input_type="number",
                description="Optional timeout (in seconds) for the request. Default is 30 seconds.",
                required=False,
                default=30,
            ),
        ]
    )
    name: str = "JupyterRunCellTool"
    description: str = (
        "Executes Python code using the Jupyter server REST API and captures stdout and stderr."
    )
    type: Literal["JupyterRunCellTool"] = "JupyterRunCellTool"

    def __call__(
        self,
        code: str,
        base_url: str,
        kernel_id: str,
        token: Optional[str] = None,
        timeout: float = 30,
    ) -> Dict[str, Any]:
        """Execute code on a Jupyter server using its REST API.

        Args:
            code (str): The Python code to execute.
            base_url (str): Base URL of the Jupyter server.
            kernel_id (str): Identifier of the kernel to execute against.
            token (Optional[str]): Authentication token for the server.
            timeout (float): Request timeout in seconds. Defaults to 30.

        Returns:
            Dict[str, Any]: A dictionary containing captured ``cell_output``,
            ``error_output`` and a ``success`` flag.

        Example:
            >>> tool = JupyterRunCellTool()
            >>> result = tool("print('hi')", "http://localhost:8888", "abcd")
        """

        logger.info("JupyterRunCellTool called with code:\n%s", code)

        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"

        url = f"{base_url.rstrip('/')}/api/kernels/{kernel_id}/execute"

        try:
            response = httpx.post(
                url,
                json={"code": code},
                headers=headers,
                timeout=timeout,
            )
            response.raise_for_status()
            data = response.json()

            cell_output = data.get("stdout", "")
            error_output = data.get("stderr", "")

            return {
                "cell_output": cell_output,
                "error_output": error_output,
                "success": True,
            }

        except HTTPError as exc:
            logger.error("HTTP request failed: %s", exc)
            return {
                "cell_output": "",
                "error_output": str(exc),
                "success": False,
            }
        except ValueError as exc:
            logger.error("Failed parsing response JSON: %s", exc)
            return {
                "cell_output": "",
                "error_output": f"Invalid response: {exc}",
                "success": False,
            }
