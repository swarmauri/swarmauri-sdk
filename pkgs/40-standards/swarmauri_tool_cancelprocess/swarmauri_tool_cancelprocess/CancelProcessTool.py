from typing import Literal

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ParameterBase import ParameterBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.processes import IProcessBackend, ProcessHandle


@ComponentBase.register_type(ToolBase, "CancelProcessTool")
class CancelProcessTool(ToolBase):
    """Cancel a running process by handle."""

    name: str = "CancelProcessTool"
    description: str = "Cancel a running process by handle."
    type: Literal["CancelProcessTool"] = "CancelProcessTool"
    backend: IProcessBackend = Field(exclude=True)
    parameters: list[ParameterBase] = Field(
        default_factory=lambda: [
            ParameterBase(
                name="process_id",
                input_type="string",
                description="Process handle",
                required=True,
            ),
        ]
    )

    def __call__(self, process_id: str) -> dict[str, bool]:
        return {"cancelled": self.backend.cancel(ProcessHandle(process_id))}
