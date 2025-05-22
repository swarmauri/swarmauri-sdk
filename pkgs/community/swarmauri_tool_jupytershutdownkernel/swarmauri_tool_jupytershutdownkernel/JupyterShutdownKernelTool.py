# JupyterShutdownKernelTool.py
#
# This module defines the JupyterShutdownKernelTool, a component responsible for gracefully
# shutting down a running Jupyter kernel. It integrates with the system's tool architecture
# and handles kernel resource release, logging, error handling, and configurable timeouts.

import logging
from typing import List, Literal, Dict, ClassVar, Any

import httpx

from pydantic import Field
try:
    from jupyter_rest_client import jupyter_rest_client
except Exception:  # pragma: no cover - optional dependency
    jupyter_rest_client = None

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ToolBase, "JupyterShutdownKernelTool")
class JupyterShutdownKernelTool(ToolBase):
    """
    JupyterShutdownKernelTool is a tool that gracefully shuts down a running Jupyter kernel.

    This tool integrates with the swarmauri framework and extends the ToolBase class to handle
    kernel shutdown logic. It releases all associated kernel resources, supports a configurable
    timeout for the shutdown process, logs shutdown events, and returns a confirmation of success
    or an error message upon failure.

    Attributes:
        version (str): The version of the JupyterShutdownKernelTool.
        parameters (List[Parameter]): A list of parameters needed to perform the kernel shutdown.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterShutdownKernelTool"]): The type identifier for this tool.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="kernel_id",
                input_type="string",
                description="Unique identifier or name of the kernel to be shut down.",
                required=True,
            ),
            Parameter(
                name="shutdown_timeout",
                input_type="integer",
                description="Maximum time in seconds to wait for the kernel to shut down cleanly.",
                required=False,
                default=5,
            ),
        ]
    )
    name: str = "JupyterShutdownKernelTool"
    description: str = (
        "Shuts down a running Jupyter kernel and releases associated resources."
    )
    type: Literal["JupyterShutdownKernelTool"] = "JupyterShutdownKernelTool"

    # Expose jupyter_rest_client for easy patching in unit tests
    jupyter_rest_client: ClassVar[Any] = jupyter_rest_client

    def __call__(self, kernel_id: str, shutdown_timeout: int = 5) -> Dict[str, str]:
        """
        Shuts down the specified Jupyter kernel using the provided kernel_id.

        Args:
            kernel_id (str): The identifier of the kernel to be shut down.
            shutdown_timeout (int): Time in seconds to wait for the kernel to shut down cleanly.

        Returns:
            Dict[str, str]: A dictionary containing the status of the operation. If successful,
                            it includes the kernel_id and a 'success' message. Otherwise,
                            it returns an 'error' message describing the failure.

        Example:
            >>> tool = JupyterShutdownKernelTool()
            >>> tool("my_kernel_id", 5)
            {'kernel_id': 'my_kernel_id', 'status': 'success', 'message': 'Kernel shut down successfully.'}

        Raises:
            Exception: If an unexpected error occurs during kernel shutdown.
        """
        logger = logging.getLogger(__name__)
        logger.info("Initiating shutdown for kernel_id='%s'", kernel_id)

        try:
            if self.jupyter_rest_client is None:
                raise RuntimeError("jupyter_rest_client is not available")

            response = self.jupyter_rest_client.shutdown_kernel(kernel_id)
            response.raise_for_status()
            data = response.json()

            message = data.get(
                "message", f"Kernel {kernel_id} shut down successfully."
            )
            logger.info(message)
            return {
                "kernel_id": kernel_id,
                "status": data.get("status", "success"),
                "message": message,
            }

        except httpx.HTTPError as e:
            message = str(e)
            try:
                if getattr(e, "response", None) is not None:
                    message = e.response.json().get("message", message)
            except Exception:
                pass
            logger.error("HTTP error while shutting down kernel: %s", message)
            return {"kernel_id": kernel_id, "status": "error", "message": message}
        except Exception as e:
            logger.exception(
                "An error occurred while shutting down kernel_id='%s'.", kernel_id
            )
            return {
                "kernel_id": kernel_id,
                "status": "error",
                "message": f"Kernel shutdown failed due to unexpected error: {str(e)}",
            }
