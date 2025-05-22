"""JupyterExecuteCellTool.py

Execute a single code cell in an active Jupyter kernel using a REST interface.

This module provides the :class:`JupyterExecuteCellTool` which delegates cell
execution to ``jupyter_rest_client``.  The tool collects output from the
kernel's IOPub WebSocket channel and returns the captured stdout, stderr and any
error information.
"""

import logging
from typing import Dict, List, Literal

import jupyter_rest_client
from pydantic import Field

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(ToolBase, "JupyterExecuteCellTool")
class JupyterExecuteCellTool(ToolBase):
    """
    JupyterExecuteCellTool sends code to an active Jupyter kernel via a REST
    interface and returns collected output messages.

    Attributes:
        version (str): The version of the JupyterExecuteCellTool.
        parameters (List[Parameter]): A list of parameters required to execute a notebook cell.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterExecuteCellTool"]): The type identifier for the tool.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="kernel_id",
                input_type="string",
                description="Identifier of the active Jupyter kernel.",
                required=True,
            ),
            Parameter(
                name="code",
                input_type="string",
                description="The code to be executed in the Jupyter kernel.",
                required=True,
            ),
        ]
    )
    name: str = "JupyterExecuteCellTool"
    description: str = "Executes code cells within a Jupyter kernel environment."
    type: Literal["JupyterExecuteCellTool"] = "JupyterExecuteCellTool"

    def __call__(self, kernel_id: str, code: str) -> Dict[str, str]:
        """Execute a code cell in the specified Jupyter kernel.

        Args:
            kernel_id (str): Identifier of the active kernel.
            code (str): The code to execute.

        Returns:
            Dict[str, str]: Captured ``stdout``, ``stderr`` and ``error`` fields.
        """

        try:
            messages = jupyter_rest_client.execute_cell(kernel_id, code)
        except Exception as exc:  # pragma: no cover - network/connection errors
            logger.error("Failed to execute cell: %s", exc)
            return {"stdout": "", "stderr": "", "error": str(exc)}

        stdout_parts: List[str] = []
        stderr_parts: List[str] = []
        error_msg = ""

        for msg in messages:
            msg_type = msg.get("msg_type")
            content = msg.get("content", {})
            if msg_type == "stream":
                if content.get("name") == "stdout":
                    stdout_parts.append(content.get("text", ""))
                elif content.get("name") == "stderr":
                    stderr_parts.append(content.get("text", ""))
            elif msg_type == "error":
                traceback_list = content.get("traceback")
                if traceback_list:
                    error_msg = "\n".join(traceback_list)
                else:
                    error_msg = f"{content.get('ename', '')}: {content.get('evalue', '')}"

        return {
            "stdout": "".join(stdout_parts),
            "stderr": "".join(stderr_parts),
            "error": error_msg,
        }

    def execute_cell(self, kernel_id: str, code: str) -> Dict[str, str]:
        """Execute the provided code cell using :meth:`__call__`."""

        return self.__call__(kernel_id, code)
