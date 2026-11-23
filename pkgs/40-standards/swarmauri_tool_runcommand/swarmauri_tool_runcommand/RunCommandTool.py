from typing import Literal

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ParameterBase import ParameterBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.processes import IProcessBackend, ProcessRequest


@ComponentBase.register_type(ToolBase, "RunCommandTool")
class RunCommandTool(ToolBase):
    """Start a command and return its process handle."""

    name: str = "RunCommandTool"
    description: str = "Start a command and return its process handle."
    type: Literal["RunCommandTool"] = "RunCommandTool"
    backend: IProcessBackend = Field(exclude=True)
    workspace: str | None = None
    parameters: list[ParameterBase] = Field(
        default_factory=lambda: [
            ParameterBase(
                name="argv",
                input_type="array",
                items={"type": "string"},
                description="Program and arguments",
                required=True,
            ),
            ParameterBase(
                name="cwd",
                input_type="string",
                description="Working directory",
                required=False,
            ),
            ParameterBase(
                name="timeout",
                input_type="number",
                description="Timeout in seconds",
                required=False,
            ),
        ]
    )

    def __call__(
        self,
        argv: list[str],
        cwd: str | None = None,
        timeout: float | None = None,
    ) -> dict[str, str]:
        handle = self.backend.start(
            ProcessRequest(
                tuple(argv),
                cwd=cwd,
                timeout=timeout,
                workspace=self.workspace,
            )
        )
        return {"process_id": handle.id}
