# JupyterShutdownKernelTool.py
#
# This module defines the JupyterShutdownKernelTool, a component responsible for gracefully
# shutting down a running Jupyter kernel. It integrates with the system's tool architecture
# and handles kernel resource release, logging, error handling, and configurable timeouts.

import logging
import time
from typing import List, Literal, Dict

from pydantic import Field
from jupyter_client import KernelManager
from jupyter_client.kernelspec import NoSuchKernel

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
            manager = KernelManager(kernel_name=kernel_id)
            # Attempt to load the connection file; if it doesn’t exist or is invalid, this may fail.
            manager.load_connection_file()

            # Request a graceful shutdown.
            manager.shutdown_kernel(now=False)
            logger.debug(
                "Shutdown request sent to kernel_id='%s'; waiting up to %s seconds.",
                kernel_id,
                shutdown_timeout,
            )

            # Wait for kernel to terminate, polling periodically.
            elapsed = 0
            poll_interval = 0.5
            while manager.is_alive() and elapsed < shutdown_timeout:
                time.sleep(poll_interval)
                elapsed += poll_interval

            # If kernel is still alive, attempt a forced shutdown.
            if manager.is_alive():
                logger.warning(
                    "Kernel did not shut down within %s seconds; forcing shutdown.",
                    shutdown_timeout,
                )
                manager.shutdown_kernel(now=True)

            # Final check to confirm kernel termination.
            if manager.is_alive():
                error_message = f"Kernel {kernel_id} could not be shut down."
                logger.error(error_message)
                return {
                    "kernel_id": kernel_id,
                    "status": "error",
                    "message": error_message,
                }

            success_message = f"Kernel {kernel_id} shut down successfully."
            logger.info(success_message)
            return {
                "kernel_id": kernel_id,
                "status": "success",
                "message": success_message,
            }

        except NoSuchKernel:
            error_message = f"No such kernel: {kernel_id}."
            logger.error(error_message)
            return {"kernel_id": kernel_id, "status": "error", "message": error_message}
        except FileNotFoundError:
            error_message = f"Connection file not found for kernel: {kernel_id}."
            logger.error(error_message)
            return {"kernel_id": kernel_id, "status": "error", "message": error_message}
        except Exception as e:
            logger.exception(
                "An error occurred while shutting down kernel_id='%s'.", kernel_id
            )
            return {
                "kernel_id": kernel_id,
                "status": "error",
                "message": f"Kernel shutdown failed due to unexpected error: {str(e)}",
            }
