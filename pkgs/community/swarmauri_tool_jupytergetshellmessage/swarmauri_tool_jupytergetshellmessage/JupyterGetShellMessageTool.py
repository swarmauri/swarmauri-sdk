from typing import ClassVar, List, Literal, Dict, Any
import logging
import time

from pydantic import Field
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
                type="number",
                description="The time in seconds to wait for shell messages before giving up.",
                required=False,
            ),
        ]
    )
    name: str = "JupyterGetShellMessageTool"
    description: str = "Retrieves messages from the Jupyter kernel's shell channel."
    type: Literal["JupyterGetShellMessageTool"] = "JupyterGetShellMessageTool"

    # Expose module-level functions/classes as class attributes for easier patching
    find_connection_file: ClassVar = find_connection_file
    BlockingKernelClient: ClassVar = BlockingKernelClient

    def __call__(self, timeout: float = 5.0) -> Dict[str, Any]:
        """
        Retrieves messages from the Jupyter kernel's shell channel within the specified timeout.

        Args:
            timeout (float, optional): The number of seconds to wait for shell messages
                                       before timing out. Defaults to 5.0.

        Returns:
            Dict[str, Any]: A dictionary containing all retrieved shell messages or an error message.
        """
        messages = []
        try:
            connection_file = (
                self.find_connection_file()
            )  # Now uses the class attribute
            client = self.BlockingKernelClient(connection_file=connection_file)
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
            logging.exception("Error retrieving shell messages")
            return {"error": str(e)}
