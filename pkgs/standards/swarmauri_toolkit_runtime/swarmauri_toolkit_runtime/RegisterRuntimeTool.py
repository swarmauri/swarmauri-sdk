from typing import Any, Dict, List, Literal, Mapping

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase
from swarmauri_standard.tools.Parameter import Parameter

from ._tool_factory import build_tool_from_spec


@ComponentBase.register_type(ToolBase, "RegisterRuntimeTool")
class RegisterRuntimeTool(ToolBase):
    version: str = "0.1.0"
    name: str = "RegisterRuntimeTool"
    description: str = (
        "Create a tool from a serialized tool spec and add it to the active toolkit."
    )
    type: Literal["RegisterRuntimeTool"] = "RegisterRuntimeTool"
    toolkit: ToolkitBase | None = Field(default=None, exclude=True, repr=False)
    protected_tool_names: set[str] = Field(
        default_factory=set, exclude=True, repr=False
    )
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="tool_spec",
                input_type="object",
                description="Serialized tool payload with 'type', 'parameters', and '__call__' fields.",
                required=True,
            )
        ]
    )

    def __call__(self, tool_spec: Mapping[str, Any] | ToolBase) -> Dict[str, Any]:
        if self.toolkit is None:
            raise ValueError("toolkit is not configured")

        tool = build_tool_from_spec(tool_spec)
        if tool.name in self.protected_tool_names:
            raise ValueError(f"Tool '{tool.name}' is reserved by RuntimeToolkit")
        if tool.name in self.toolkit.tools:
            raise ValueError(f"Tool '{tool.name}' already exists in the toolkit")

        self.toolkit.add_tool(tool)
        return {
            "status": "created",
            "tool_name": tool.name,
            "tool_type": tool.type,
            "tool": tool.model_dump(exclude_none=True, by_alias=True),
            "tool_count": len(self.toolkit),
        }
