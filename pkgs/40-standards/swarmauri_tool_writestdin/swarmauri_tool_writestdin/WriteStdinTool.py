from typing import Literal

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ParameterBase import ParameterBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.processes import IProcessBackend, ProcessHandle


@ComponentBase.register_type(ToolBase, "WriteStdinTool")
class WriteStdinTool(ToolBase):
    """Write text to an existing process or close its input."""

    name: str = "WriteStdinTool"
    description: str = "Write text to an existing process or close its input."
    type: Literal["WriteStdinTool"] = "WriteStdinTool"
    backend: IProcessBackend = Field(exclude=True)
    parameters: list[ParameterBase] = Field(
        default_factory=lambda: [
            ParameterBase(
                name="process_id",
                input_type="string",
                description="Process handle",
                required=True,
            ),
            ParameterBase(
                name="text",
                input_type="string",
                description="Text to write",
                required=False,
            ),
            ParameterBase(
                name="close",
                input_type="boolean",
                description="Close stdin after writing",
                required=False,
            ),
        ]
    )

    def __call__(
        self, process_id: str, text: str = "", close: bool = False
    ) -> dict[str, bool]:
        self.backend.write_stdin(
            ProcessHandle(process_id), text.encode(), close=close
        )
        return {"written": True}
