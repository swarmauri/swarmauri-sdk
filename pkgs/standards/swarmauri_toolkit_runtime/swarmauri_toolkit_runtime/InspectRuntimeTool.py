from typing import Any, Dict, List, Literal

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase
from swarmauri_standard.tools.Parameter import Parameter


@ComponentBase.register_type(ToolBase, "InspectRuntimeTool")
class InspectRuntimeTool(ToolBase):
    version: str = "0.1.0"
    name: str = "InspectRuntimeTool"
    description: str = "Read one tool from the active toolkit by name."
    type: Literal["InspectRuntimeTool"] = "InspectRuntimeTool"
    toolkit: ToolkitBase | None = Field(default=None, exclude=True, repr=False)
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="tool_name",
                input_type="string",
                description="Name of the tool to fetch from the toolkit.",
                required=True,
            )
        ]
    )

    def __call__(self, tool_name: str) -> Dict[str, Any]:
        if self.toolkit is None:
            raise ValueError("toolkit is not configured")

        tool = self.toolkit.get_tool_by_name(tool_name)
        return {
            "tool_name": tool_name,
            "tool_type": tool.type,
            "tool": tool.model_dump(exclude_none=True),
        }
