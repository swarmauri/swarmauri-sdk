from typing import Any, Dict, ClassVar
import logging
import time

from jupyter_client import find_connection_file, BlockingKernelClient

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(ToolBase, "JupyterExecuteCellTool")
class JupyterExecuteCellTool(ToolBase):
    """
    JupyterExecuteCellTool executes a cell on a Jupyter kernel and returns the output.
    It properly handles cases where no active kernel is available or when an exception occurs.
    """

    version: str = "1.0.0"
    parameters = [
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
    type: str = "JupyterExecuteCellTool"

    # Expose module-level functions/classes as class attributes for easier patching in tests.
    find_connection_file: ClassVar = find_connection_file
    BlockingKernelClient: ClassVar = BlockingKernelClient

    def __call__(self, cell: str, timeout: float = 5.0) -> Dict[str, Any]:
        try:
            # Use the class attribute to allow patching
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
