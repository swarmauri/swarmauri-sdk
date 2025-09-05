"""
SubprocessTool.py

Provides a tool for executing shell commands via Python's ``subprocess`` module.
It captures the command's output and exit status and returns them in a
structured dictionary.
"""

import shlex
import subprocess
from typing import List, Literal, Dict, Optional
from pydantic import Field

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ToolBase, "SubprocessTool")
class SubprocessTool(ToolBase):
    """Execute a shell command and return its output."""

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="command",
                input_type="string",
                description="Command to execute",
                required=True,
            ),
            Parameter(
                name="timeout",
                input_type="number",
                description="Optional timeout in seconds",
                required=False,
            ),
            Parameter(
                name="shell",
                input_type="boolean",
                description="Run command through the shell",
                required=False,
            ),
        ]
    )
    name: str = "SubprocessTool"
    description: str = "Executes a command in a subprocess and captures its output."
    type: Literal["SubprocessTool"] = "SubprocessTool"

    def __call__(
        self, command: str, timeout: Optional[float] = None, shell: bool = False
    ) -> Dict[str, str]:
        """Execute ``command`` and return stdout, stderr, and exit code."""
        try:
            result = subprocess.run(
                command if shell else shlex.split(command),
                capture_output=True,
                text=True,
                shell=shell,
                timeout=timeout,
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": str(result.returncode),
            }
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": "Process timed out",
                "exit_code": "timeout",
            }
        except Exception as e:  # pragma: no cover - fallback error handling
            return {
                "stdout": "",
                "stderr": str(e),
                "exit_code": "error",
            }
