"""
SubprocessTool.py

Provide a tool for executing shell commands via Python's ``subprocess``
module.

This module exposes ``SubprocessTool``, a first-class Swarmauri tool that
runs a command in a subprocess and returns a structured result containing
``status``, ``stdout``, ``stderr``, and ``exit_code``. It defaults to
``shell=False`` to prevent shell injection and supports both string
commands (split via ``shlex``) and explicit argument vectors.
"""

import shlex
import subprocess
from typing import Dict, List, Literal, Optional, Union

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase  # type: ignore[import-untyped]
from swarmauri_base.tools.ParameterBase import ParameterBase  # type: ignore[import-untyped]
from swarmauri_base.tools.ToolBase import ToolBase  # type: ignore[import-untyped]

@ComponentBase.register_type(ToolBase, "SubprocessTool")
class SubprocessTool(ToolBase):  # type: ignore[misc]
    """
    Execute a shell command and return its output.

    This tool wraps Python's ``subprocess`` module and returns a
    structured dictionary containing the captured ``stdout``, ``stderr``,
    and ``exit_code``. Runtime failures such as timeouts and missing
    executables are surfaced through a ``status`` field instead of raising
    exceptions, keeping execution results distinguishable from tool or
    runtime errors.

    Attributes:
        version (str): The tool version.
        parameters (List[ParameterBase]): The declared tool parameters.
        name (str): The registered tool name.
        description (str): A human-readable description of the tool.
        type (Literal["SubprocessTool"]): The component type discriminator.
    """

    version: str = "1.0.0"
    parameters: List[ParameterBase] = Field(
        default_factory=lambda: [
            ParameterBase(
                name="command",
                input_type="string",
                description="Command to execute",
                required=True,
            ),
            ParameterBase(
                name="timeout",
                input_type="number",
                description="Optional timeout in seconds",
                required=False,
            ),
            ParameterBase(
                name="shell",
                input_type="boolean",
                description="Run command through the shell",
                required=False,
            ),
            ParameterBase(
                name="cwd",
                input_type="string",
                description="Working directory",
                required=False,
            ),
        ]
    )
    name: str = "SubprocessTool"
    description: str = (
        "Executes a command in a subprocess and captures its output."
    )
    type: Literal["SubprocessTool"] = "SubprocessTool"

    def __call__(
        self,
        command: Union[str, List[str]],
        timeout: Optional[float] = None,
        shell: bool = False,
        cwd: Optional[str] = None,
    ) -> Dict[str, Union[str, int, None]]:
        """
        Execute a command and return its stdout, stderr, and exit code.

        Support both string commands (split via ``shlex.split``) and
        argument vectors (list of strings). Default to ``shell=False`` to
        prevent shell injection. Non-zero exit codes are preserved without
        being conflated with tool or runtime failures; timeouts and missing
        executables are reported via the ``status`` field.

        Args:
            command (Union[str, List[str]]): The command to execute. Pass a
                list of strings to avoid shell parsing entirely.
            timeout (Optional[float]): Optional timeout in seconds. A
                ``status`` of ``"timeout"`` is returned on expiry.
            shell (bool): Whether to run the command through the platform
                shell. Defaults to ``False``.
            cwd (Optional[str]): Optional working directory for the
                subprocess.

        Returns:
            Dict[str, Union[str, int, None]]: A dictionary containing
                ``status`` (``"success"``, ``"timeout"``, ``"not_found"``,
                or ``"runtime_error"``), ``stdout``, ``stderr``, and
                ``exit_code``.
        """
        if isinstance(command, str):
            if shell:
                args: Union[str, List[str]] = command
            else:
                args = shlex.split(command)
        else:
            args = command

        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                shell=shell,
                check=False,
                timeout=timeout,
                cwd=cwd,
            )
            return {
                "status": "success",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "stdout": "",
                "stderr": f"Process timed out after {timeout} seconds",
                "exit_code": None,
            }
        except FileNotFoundError:
            return {
                "status": "not_found",
                "stdout": "",
                "stderr": (
                    "Executable not found: "
                    f"{args[0] if isinstance(args, list) else args}"
                ),
                "exit_code": 127,
            }
        except Exception as e:
            return {
                "status": "runtime_error",
                "stdout": "",
                "stderr": str(e),
                "exit_code": None,
            }