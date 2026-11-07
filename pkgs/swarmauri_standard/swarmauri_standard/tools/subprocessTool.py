"""Preserve the original subprocess import and string result contract."""

import warnings
from typing import Any

__all__ = ["SubprocessTool"]  # noqa: F822 - supplied by module __getattr__


def __getattr__(name: str) -> Any:
    """Load the legacy adapter on first access."""
    if name != "SubprocessTool":
        raise AttributeError(f"module {__name__} has no attribute {name}")

    warnings.warn(
        "swarmauri_standard.tools.SubprocessTool is deprecated; "
        "use swarmauri_tool_subprocess for typed execution results.",
        DeprecationWarning,
        stacklevel=2,
    )
    from typing import Literal

    from pydantic import Field
    from swarmauri_base.tools.ToolBase import ToolBase

    from . import _subprocess
    from .Parameter import Parameter

    class SubprocessTool(ToolBase):
        """Adapt results for callers of the original standard tool."""

        version: str = "1.0.0"
        parameters: list[Parameter] = Field(
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
        description: str = (
            "Executes a command in a subprocess and captures its output."
        )
        type: Literal["SubprocessTool"] = "SubprocessTool"

        def __call__(
            self,
            command: str,
            timeout: float | None = None,
            shell: bool = False,
        ) -> dict[str, str]:
            result = _subprocess.run_subprocess(
                command, timeout=timeout, shell=shell
            )
            if result["status"] == "success":
                exit_code = str(result["exit_code"])
                stderr = str(result["stderr"])
            elif result["status"] == "timeout":
                exit_code = "timeout"
                stderr = "Process timed out"
            else:
                exit_code = "error"
                stderr = str(result["stderr"])
            return {
                "stdout": str(result["stdout"]),
                "stderr": stderr,
                "exit_code": exit_code,
            }

    # Do not register the adapter over the standalone component type.
    SubprocessTool.__qualname__ = "SubprocessTool"
    return globals().setdefault(name, SubprocessTool)
