from typing import Any, Dict, List, Literal, Mapping

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase
from swarmauri_standard.tools.Parameter import Parameter

from ._tool_factory import build_tool_from_spec


@ComponentBase.register_type(ToolBase, "ReplaceRuntimeTool")
class ReplaceRuntimeTool(ToolBase):
    version: str = "0.1.0"
    name: str = "ReplaceRuntimeTool"
    description: str = "Replace an existing non-reserved tool in the active toolkit with a new serialized tool spec."
    type: Literal["ReplaceRuntimeTool"] = "ReplaceRuntimeTool"
    toolkit: ToolkitBase | None = Field(default=None, exclude=True, repr=False)
    protected_tool_names: set[str] = Field(
        default_factory=set, exclude=True, repr=False
    )
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="tool_name",
                input_type="string",
                description="Existing tool name to replace.",
                required=True,
            ),
            Parameter(
                name="tool_spec",
                input_type="object",
                description="Serialized replacement tool payload with at least a 'type' field.",
                required=True,
            ),
        ]
    )

    def __call__(
        self, tool_name: str, tool_spec: Mapping[str, Any] | ToolBase
    ) -> Dict[str, Any]:
        if self.toolkit is None:
            raise ValueError("toolkit is not configured")
        if tool_name in self.protected_tool_names:
            raise ValueError(f"Tool '{tool_name}' is reserved by RuntimeToolkit")
        if tool_name not in self.toolkit.tools:
            raise ValueError(f"Tool '{tool_name}' not found in the toolkit")

        replacement = build_tool_from_spec(tool_spec)
        if (
            replacement.name in self.protected_tool_names
            and replacement.name != tool_name
        ):
            raise ValueError(f"Tool '{replacement.name}' is reserved by RuntimeToolkit")
        if replacement.name != tool_name and replacement.name in self.toolkit.tools:
            raise ValueError(f"Tool '{replacement.name}' already exists in the toolkit")

        self.toolkit.remove_tool(tool_name)
        self.toolkit.add_tool(replacement)
        return {
            "status": "updated",
            "previous_tool_name": tool_name,
            "tool_name": replacement.name,
            "tool_type": replacement.type,
            "tool": replacement.model_dump(exclude_none=True),
            "tool_count": len(self.toolkit),
        }
