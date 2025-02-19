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
    Retrieves messages from the Jupyter kernel's shell channel.
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

    # Expose functions as class attributes for easier patching
    find_connection_file: ClassVar = find_connection_file
    BlockingKernelClient: ClassVar = BlockingKernelClient

    def __call__(self, timeout: float = 5.0) -> Dict[str, Any]:
        messages = []
        try:
            connection_file = self.find_connection_file()
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
            logger.exception("Error retrieving shell messages")
            return {"error": str(e)}


@ComponentBase.register_type(ToolBase, "JupyterExecuteCellTool")
class JupyterExecuteCellTool(ToolBase):
    """
    Executes a cell on a Jupyter kernel and returns the output.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = [
        Parameter(
            name="cell",
            type="string",
            description="Cell code to execute.",
            required=True,
        ),
        Parameter(
            name="timeout",
            type="number",
            description="Time in seconds to wait for a response.",
            required=False,
        ),
    ]
    name: str = "JupyterExecuteCellTool"
    description: str = "Executes a cell on a Jupyter kernel and returns the output."
    type: Literal["JupyterExecuteCellTool"] = "JupyterExecuteCellTool"

    # Expose functions as class attributes for easier patching in tests.
    find_connection_file: ClassVar = find_connection_file
    BlockingKernelClient: ClassVar = BlockingKernelClient

    def __call__(self, cell: str, timeout: float = 5.0) -> Dict[str, Any]:
        try:
            connection_file = self.find_connection_file()
            client = self.BlockingKernelClient(connection_file=connection_file)
            client.load_connection_file()
            client.start_channels()

            client.execute(cell)
            start_time = time.monotonic()
            output = None

            # Wait for an "execute_reply" message
            while time.monotonic() - start_time < timeout:
                if client.shell_channel.msg_ready():
                    msg = client.shell_channel.get_msg(block=False)
                    if msg.get("header", {}).get("msg_type") == "execute_reply":
                        output = msg
                        break
                else:
                    time.sleep(0.1)

            client.stop_channels()

            if output is None:
                error_msg = (
                    f"No response received from the kernel within {timeout} seconds."
                )
                logger.error(error_msg)
                return {"error": error_msg}

            return {"output": output}

        except Exception as e:
            logger.exception("Error executing cell")
            return {"error": str(e)}
