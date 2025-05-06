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
from typing import List, Literal, Dict, Optional, Any, ClassVar
from pydantic import Field
from jupyter_client import KernelManager

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(ToolBase, "JupyterStartKernelTool")
class JupyterStartKernelTool(ToolBase):
    """
    JupyterStartKernelTool is a tool that initializes and configures a Jupyter kernel instance.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="kernel_name",
                input_type="string",
                description="The name of the Jupyter kernel to start (e.g., 'python3').",
                required=False,
                default="python3",
            ),
            Parameter(
                name="kernel_spec",
                input_type="object",
                description="Optional dictionary to configure kernel specifications (if supported).",
                required=False,
                default=None,
            ),
        ]
    )
    name: str = "JupyterStartKernelTool"
    description: str = "Initializes and configures a Jupyter kernel instance."
    type: Literal["JupyterStartKernelTool"] = "JupyterStartKernelTool"

    # Expose KernelManager for patching in tests
    KernelManager: ClassVar = KernelManager

    def __call__(
        self, kernel_name: str = "python3", kernel_spec: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Starts a new Jupyter kernel instance with the provided kernel name and optional specifications.
        """
        try:
            # Initialize the kernel manager using the class attribute
            km = KernelManager(kernel_name=kernel_name)

            if kernel_spec:
                logger.debug(f"Applying kernel specification: {kernel_spec}")

            km.start_kernel()
            kernel_id = km.kernel_id

            # Store the KernelManager for further interactions
            self._kernel_manager = km

            # Log the successful start
            logger.info(
                f"Started Jupyter kernel '{kernel_name}' with ID '{kernel_id}'."
            )
            return {"kernel_name": kernel_name, "kernel_id": kernel_id}

        except Exception as ex:
            logger.error(f"Failed to start Jupyter kernel '{kernel_name}': {ex}")
            # Ensure that we don't store an invalid manager
            self._kernel_manager = None
            return {"error": str(ex)}

    def get_kernel_manager(self) -> Optional[KernelManager]:
        """
        Retrieves the KernelManager instance for the active Jupyter kernel.
        """
        return getattr(self, "_kernel_manager", None)
