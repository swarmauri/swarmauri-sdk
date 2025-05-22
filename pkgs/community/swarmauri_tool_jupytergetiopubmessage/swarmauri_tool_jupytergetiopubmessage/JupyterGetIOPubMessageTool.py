from typing import List, Dict, Any, Literal
from pydantic import Field
import time
import json
import logging
import importlib

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(ToolBase, "JupyterGetIOPubMessageTool")
class JupyterGetIOPubMessageTool(ToolBase):
    """
    JupyterGetIOPubMessageTool is responsible for retrieving IOPub messages from an active
    Jupyter kernel within a specified timeout. It captures output, errors, and logging
    information from executed cells, and returns the collected data for further processing.

    The tool integrates with cell execution tools to enable complete output capture and
    logs IOPub retrieval events for debugging. Timeouts and message parsing errors are handled
    gracefully, ensuring robust communication with the Jupyter kernel.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="channels_url",
                input_type="string",
                description=(
                    "WebSocket URL for the kernel channels endpoint (/api/kernels/{id}/channels)."
                ),
                required=True,
            ),
            Parameter(
                name="timeout",
                input_type="number",
                description="Time (in seconds) to wait for incoming IOPub messages before timing out.",
                required=False,
                default=5.0,
            ),
        ]
    )
    name: str = "JupyterGetIOPubMessageTool"
    description: str = (
        "Retrieves IOPub messages from a Jupyter kernel with a specified timeout."
    )
    type: Literal["JupyterGetIOPubMessageTool"] = "JupyterGetIOPubMessageTool"

    def __call__(self, channels_url: str, timeout: float = 5.0) -> Dict[str, Any]:
        """
        Retrieve IOPub messages from the kernel's WebSocket ``channels`` endpoint.

        This method connects to ``/api/kernels/{id}/channels`` via WebSocket and
        listens for messages until the kernel becomes idle or the timeout
        expires. Message parsing errors are logged and collected.

        Args:
            channels_url (str): WebSocket URL to ``/api/kernels/{id}/channels``.
            timeout (float, optional): Time in seconds to wait for IOPub messages. Defaults to 5.0.

        Returns:
            Dict[str, Any]: A dictionary containing captured outputs. The dictionary includes:
                - "stdout": List of standard output messages
                - "stderr": List of error messages
                - "logs": List of logging or debug messages
                - "execution_results": List of any returned execution data (e.g., from 'execute_result')
                - "timeout_exceeded": Boolean indicating whether a timeout occurred

        Example:
            >>> tool = JupyterGetIOPubMessageTool()
            >>> result = tool(
            ...     "ws://localhost:8888/api/kernels/12345/channels",
            ...     timeout=3.0,
            ... )
            >>> print(result["stdout"])
            ['Hello world!']
        """
        logger.debug(
            "Starting retrieval of IOPub messages with a timeout of %s seconds.",
            timeout,
        )
        start_time = time.time()

        websocket_module = importlib.import_module("websocket")
        ws = websocket_module.create_connection(channels_url, timeout=timeout)
        ws.settimeout(0.1)

        # Containers for captured data
        stdout_messages = []
        stderr_messages = []
        logs = []
        execution_results = []

        try:
            # Continue to retrieve messages until idle or timeout
            while True:
                # Check elapsed time for timeout
                if (time.time() - start_time) > timeout:
                    logger.warning("Timeout exceeded while waiting for IOPub messages.")
                    return {
                        "stdout": stdout_messages,
                        "stderr": stderr_messages,
                        "logs": logs,
                        "execution_results": execution_results,
                        "timeout_exceeded": True,
                    }

                try:
                    raw_msg = ws.recv()
                except websocket_module.WebSocketTimeoutException:
                    continue

                try:
                    msg = json.loads(raw_msg)
                except Exception as exc:
                    logger.error("Error parsing IOPub message: %s", str(exc))
                    logs.append({"error": f"Error parsing IOPub message: {str(exc)}"})
                    continue

                msg_type = msg["msg_type"]
                msg_content = msg["content"]
                logger.debug("Received IOPub message of type '%s'.", msg_type)

                # Handle message based on its type
                if msg_type == "stream":
                    # Typically captures stdout or stderr output
                    if msg_content.get("name") == "stdout":
                        stdout_messages.append(msg_content.get("text", ""))
                    elif msg_content.get("name") == "stderr":
                        stderr_messages.append(msg_content.get("text", ""))
                elif msg_type == "execute_result":
                    # Captures the main result of an executed cell
                    execution_results.append(msg_content.get("data", {}))
                elif msg_type == "display_data":
                    # Captures display data from executed cell
                    execution_results.append(msg_content.get("data", {}))
                elif msg_type == "error":
                    # Captures error messages
                    traceback = msg_content.get("traceback", [])
                    error_message = (
                        "\n".join(traceback)
                        if traceback
                        else msg_content.get("evalue", "")
                    )
                    stderr_messages.append(error_message)
                elif msg_type == "status":
                    # Status updates: 'busy', 'idle', etc.
                    execution_state = msg_content.get("execution_state", "")
                    if execution_state == "idle":
                        # Kernel is done processing
                        logger.debug(
                            "Kernel reported idle state. Stopping message capture."
                        )
                        break
                else:
                    # Other messages (e.g., clear_output, update_display_data) can be logged
                    logs.append({"type": msg_type, "content": msg_content})

        finally:
            ws.close()

        # Successfully captured messages without timeout
        return {
            "stdout": stdout_messages,
            "stderr": stderr_messages,
            "logs": logs,
            "execution_results": execution_results,
            "timeout_exceeded": False,
        }
