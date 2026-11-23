from typing import Literal

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ParameterBase import ParameterBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.processes import IProcessBackend, ProcessHandle


@ComponentBase.register_type(ToolBase, "ReadProcessOutputTool")
class ReadProcessOutputTool(ToolBase):
    """Read process output from a continuation cursor."""

    name: str = "ReadProcessOutputTool"
    description: str = "Read process output from a continuation cursor."
    type: Literal["ReadProcessOutputTool"] = "ReadProcessOutputTool"
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
                name="after",
                input_type="integer",
                description="Previous cursor",
                required=False,
            ),
            ParameterBase(
                name="wait",
                input_type="number",
                description="Seconds to wait for output",
                required=False,
            ),
            ParameterBase(
                name="release",
                input_type="boolean",
                description="Release a completed process after reading",
                required=False,
            ),
        ]
    )

    def __call__(
        self,
        process_id: str,
        after: int = 0,
        wait: float = 0,
        release: bool = False,
    ) -> dict:
        handle = ProcessHandle(process_id)
        page = self.backend.read(handle, after=after, wait=wait)
        events = [
            {
                "sequence": event.sequence,
                "kind": event.kind,
                "text": event.data.decode("utf-8", errors="replace"),
                "exit_code": event.exit_code,
                "outcome": event.outcome,
            }
            for event in page.events
        ]
        if release and page.events and page.events[-1].kind == "exit":
            self.backend.release(handle)
        return {
            "events": events,
            "cursor": page.cursor,
            "truncated": page.truncated,
        }
