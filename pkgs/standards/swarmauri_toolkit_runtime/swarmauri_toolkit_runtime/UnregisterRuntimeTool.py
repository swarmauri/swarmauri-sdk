from typing import Any, Dict, List, Literal

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase
from swarmauri_standard.tools.Parameter import Parameter


@ComponentBase.register_type(ToolBase, "UnregisterRuntimeTool")
class UnregisterRuntimeTool(ToolBase):
    version: str = "0.1.0"
    name: str = "UnregisterRuntimeTool"
    description: str = "Delete a non-reserved tool from the active toolkit."
    type: Literal["UnregisterRuntimeTool"] = "UnregisterRuntimeTool"
    toolkit: ToolkitBase | None = Field(default=None, exclude=True, repr=False)
    protected_tool_names: set[str] = Field(
        default_factory=set, exclude=True, repr=False
    )
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="tool_name",
                input_type="string",
                description="Name of the tool to remove from the toolkit.",
                required=True,
            )
        ]
    )

    def __call__(self, tool_name: str) -> Dict[str, Any]:
        if self.toolkit is None:
            raise ValueError("toolkit is not configured")
        if tool_name in self.protected_tool_names:
            raise ValueError(
                f"Tool '{tool_name}' is reserved by RuntimeToolkit"
            )

        self.toolkit.remove_tool(tool_name)
        return {
            "status": "deleted",
            "tool_name": tool_name,
            "tool_count": len(self.toolkit),
        }
