from typing import ClassVar, Callable, Any, Dict, List, Literal
import logging
import time

from pydantic import Field, PrivateAttr
from jupyter_client import find_connection_file, BlockingKernelClient

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(ToolBase, "JupyterGetShellMessageTool")
class JupyterGetShellMessageTool(ToolBase):
    """
    JupyterGetShellMessageTool is a tool designed to retrieve messages from the kernel's shell channel.
    It listens for shell messages within a specified timeout, logs them for diagnostics, and returns
    the structured messages.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="timeout",
                input_type="number",
                description="The time in seconds to wait for shell messages before giving up.",
                required=False,
            ),
        ]
    )
    name: str = "JupyterGetShellMessageTool"
    description: str = "Retrieves messages from the Jupyter kernel's shell channel."
    type: Literal["JupyterGetShellMessageTool"] = "JupyterGetShellMessageTool"

    # Public class attributes for patching.
    find_connection_file: ClassVar[Callable[[], str]] = staticmethod(
        find_connection_file
    )
    BlockingKernelClient: ClassVar[Callable[..., Any]] = BlockingKernelClient

    # Private attributes to hold the patched functions.
    _find_connection_file: Callable[[], str] = PrivateAttr(
        default_factory=lambda: JupyterGetShellMessageTool.find_connection_file
    )
    _BlockingKernelClient: Callable[..., Any] = PrivateAttr(
        default_factory=lambda: JupyterGetShellMessageTool.BlockingKernelClient
    )

    def __init__(self, **data: Any):
        super().__init__(**data)
        # Add the patched functions to private attributes.
        self._find_connection_file = self.__class__.find_connection_file
        self._BlockingKernelClient = self.__class__.BlockingKernelClient

    def __call__(self, timeout: float = 5.0) -> Dict[str, Any]:
        messages = []
        try:
            # Use the private attribute that now holds the patched find_connection_file.
            connection_file = self._find_connection_file()
            client = self._BlockingKernelClient(connection_file=connection_file)
            client.load_connection_file()
            client.start_channels()

            start_time = time.monotonic()
            retrieved_any_message = False

            while time.monotonic() - start_time < timeout:
                if client.shell_channel.msg_ready():
                    msg = client.shell_channel.get_msg(block=False)
                    messages.append(msg)
                    logging.debug(f"Retrieved a shell message: {msg}")
                    retrieved_any_message = True
                else:
                    time.sleep(0.1)

            client.stop_channels()

            if not retrieved_any_message:
                return {
                    "error": f"No shell messages received within {timeout} seconds."
                }

            return {"messages": messages}

        except Exception as e:
            logger.exception("Error retrieving shell messages")
            return {"error": str(e)}
