from typing import Any, Dict, List, Literal

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase


@ComponentBase.register_type(ToolBase, "ListToolkitToolsTool")
class ListToolkitToolsTool(ToolBase):
    version: str = "0.1.0"
    name: str = "ListToolkitToolsTool"
    description: str = "List all tools currently available in the active toolkit."
    type: Literal["ListToolkitToolsTool"] = "ListToolkitToolsTool"
    toolkit: ToolkitBase | None = Field(default=None, exclude=True, repr=False)
    parameters: List[Any] = Field(default_factory=list)

    def __call__(self) -> Dict[str, Any]:
        if self.toolkit is None:
            raise ValueError("toolkit is not configured")

        tools = {
            name: tool.model_dump(exclude_none=True)
            for name, tool in self.toolkit.tools.items()
        }
        return {
            "tool_count": len(self.toolkit),
            "tool_names": list(self.toolkit.tools.keys()),
            "tools": tools,
        }
