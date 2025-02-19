"""
JupyterStartKernelTool.py

This module defines the JupyterStartKernelTool, a component that starts a Jupyter kernel instance.
It leverages the ToolBase and ComponentBase classes from the swarmauri framework to integrate
seamlessly with the system's tool architecture.

The JupyterStartKernelTool supports initializing and configuring a new Jupyter kernel instance,
logging kernel start events, handling startup errors gracefully, and returning the kernel ID for
reference. It can also integrate with further tools that execute cells within the started kernel.
"""

import logging
from typing import List, Literal, Dict, Optional, Any
from pydantic import Field
from jupyter_client import KernelManager

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_core.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(ToolBase, "JupyterStartKernelTool")
class JupyterStartKernelTool(ToolBase):
    """
    JupyterStartKernelTool is a tool that initializes and configures a Jupyter kernel instance.

    Attributes:
        version (str): The version of the JupyterStartKernelTool.
        parameters (List[Parameter]): A list of parameters that define how the Jupyter kernel
                                      will be initialized.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterStartKernelTool"]): The type identifier for this tool.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="kernel_name",
                type="string",
                description="The name of the Jupyter kernel to start (e.g., 'python3').",
                required=False,
                default="python3",
            ),
            Parameter(
                name="kernel_spec",
                type="object",
                description="Optional dictionary to configure kernel specifications (if supported).",
                required=False,
                default=None,
            ),
        ]
    )
    name: str = "JupyterStartKernelTool"
    description: str = "Initializes and configures a Jupyter kernel instance."
    type: Literal["JupyterStartKernelTool"] = "JupyterStartKernelTool"

    def __call__(
        self, kernel_name: str = "python3", kernel_spec: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Starts a new Jupyter kernel instance with the provided kernel name and optional specifications.

        Args:
            kernel_name (str): The name of the Jupyter kernel to start. Defaults to "python3".
            kernel_spec (Optional[Dict[str, Any]]): Optional dictionary of kernel configuration settings.

        Returns:
            Dict[str, str]: A dictionary containing either the 'kernel_id' key with the kernel's identifier
                            and 'kernel_name', or an 'error' key if the startup fails.
        """
        try:
            # Initialize the kernel manager
            km = KernelManager(kernel_name=kernel_name)

            # If there are kernel specifications to apply, handle them here
            if kernel_spec:
                # Example placeholder for applying additional configuration
                # (In practice, you might apply environment variables or other settings)
                logger.debug(f"Applying kernel specification: {kernel_spec}")

            # Start the kernel
            km.start_kernel()
            kernel_id = km.kernel_id

            # Store the KernelManager for potential further interactions
            self._kernel_manager = km

            # Log the successful start
            logger.info(
                f"Started Jupyter kernel '{kernel_name}' with ID '{kernel_id}'."
            )
            return {"kernel_name": kernel_name, "kernel_id": kernel_id}

        except Exception as ex:
            # Log and return error details
            logger.error(f"Failed to start Jupyter kernel '{kernel_name}': {ex}")
            return {"error": str(ex)}

    def get_kernel_manager(self) -> Optional[KernelManager]:
        """
        Retrieves the KernelManager instance for the active Jupyter kernel.

        Returns:
            Optional[KernelManager]: The KernelManager instance if a kernel is running, otherwise None.
        """
        return getattr(self, "_kernel_manager", None)
