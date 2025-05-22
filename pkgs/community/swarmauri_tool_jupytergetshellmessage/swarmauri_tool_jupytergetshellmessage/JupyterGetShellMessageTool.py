"""
JupyterGetShellMessageTool.py
This module defines the JupyterGetShellMessageTool, a component that retrieves messages
from the Jupyter kernel's shell channel. It leverages the ToolBase and ComponentBase
classes from the swarmauri framework to integrate with the system's tool architecture.
The JupyterGetShellMessageTool supports retrieving and parsing messages for diagnostic
purposes. It includes timeout-based handling to avoid hanging during message retrieval.
"""

from typing import ClassVar, Callable, Any, Dict, List, Literal
import json
import logging
import time

from pydantic import Field, PrivateAttr
from jupyter_client import find_connection_file
from websocket import create_connection

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(ToolBase, "JupyterGetShellMessageTool")
class JupyterGetShellMessageTool(ToolBase):
    """
    JupyterGetShellMessageTool is a tool designed to retrieve messages from the kernel's shell channel.
    It listens for shell messages within a specified timeout, logs them for diagnostics, and returns
    the structured messages.

    Attributes:
        version (str): The version of the JupyterGetShellMessageTool.
        parameters (List[Parameter]): A list of parameters that configure message retrieval.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterGetShellMessageTool"]): The type identifier for the tool.
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
    create_connection: ClassVar[Callable[..., Any]] = staticmethod(create_connection)
    read_json_file: ClassVar[Callable[[str], Dict[str, Any]]] = staticmethod(
        lambda p: json.load(open(p))
    )
    build_ws_url: ClassVar[Callable[[Dict[str, Any]], str]] = staticmethod(
        lambda info: info.get("ws_url", "")
    )

    # Private attributes to hold the patched functions.
    _find_connection_file: Callable[[], str] = PrivateAttr(
        default_factory=lambda: JupyterGetShellMessageTool.find_connection_file
    )
    _create_connection: Callable[..., Any] = PrivateAttr(
        default_factory=lambda: JupyterGetShellMessageTool.create_connection
    )
    _read_json_file: Callable[[str], Dict[str, Any]] = PrivateAttr(
        default_factory=lambda: JupyterGetShellMessageTool.read_json_file
    )
    _build_ws_url: Callable[[Dict[str, Any]], str] = PrivateAttr(
        default_factory=lambda: JupyterGetShellMessageTool.build_ws_url
    )

    def __call__(self, timeout: float = 5.0) -> Dict[str, Any]:
        """
        Retrieves messages from the Jupyter kernel's shell channel within the specified timeout.
        Args:
            timeout (float, optional): The number of seconds to wait for shell messages
                                    before timing out. Defaults to 5.0.

        Returns:
            Dict[str, Any]: A dictionary containing all retrieved shell messages or an error message.

        Example:
            >>> tool = JupyterGetShellMessageTool()
            >>> result = tool(timeout=10.0)
            >>> print(result)
            {
                'messages': [
                    {'header': {...}, 'parent_header': {...}, 'metadata': {...}, 'content': {...}, 'buffers': [...]},
                    ...
                ]
            }
        """
        messages = []
        try:
            connection_file = self._find_connection_file()
            connection_info = self._read_json_file(connection_file)
            ws_url = self._build_ws_url(connection_info)
            ws = self._create_connection(ws_url)
            ws.settimeout(0.1)

            start_time = time.monotonic()

            while time.monotonic() - start_time < timeout:
                try:
                    raw_msg = ws.recv()
                except Exception:
                    time.sleep(0.1)
                    continue

                if not raw_msg:
                    continue

                try:
                    msg = json.loads(raw_msg)
                except Exception:
                    logger.debug("Failed to decode message: %s", raw_msg)
                    continue

                messages.append(msg)

            ws.close()

            if not messages:
                return {
                    "error": f"No shell messages received within {timeout} seconds."
                }

            return {"messages": messages}

        except Exception as e:
            logger.exception("Error retrieving shell messages")
            return {"error": str(e)}
