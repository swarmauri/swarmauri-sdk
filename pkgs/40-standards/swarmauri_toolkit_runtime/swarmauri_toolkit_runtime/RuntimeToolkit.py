from collections.abc import Callable, Mapping
from typing import Dict, Literal

from pydantic import Field, PrivateAttr

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase

from .RegisterRuntimeTool import RegisterRuntimeTool
from .InspectRuntimeTool import InspectRuntimeTool
from .ListRuntimeTools import ListRuntimeTools
from .UnregisterRuntimeTool import UnregisterRuntimeTool
from .ReplaceRuntimeTool import ReplaceRuntimeTool
from .RecipeTool import RecipeTool
from ._tool_factory import build_tool_from_spec


@ComponentBase.register_type(ToolkitBase, "RuntimeToolkit")
class RuntimeToolkit(ToolkitBase):
    type: Literal["RuntimeToolkit"] = "RuntimeToolkit"
    tools: Dict[str, ToolBase] = {}
    revision: int = Field(default=0, ge=0)
    _recipe_dispatch: Callable | None = PrivateAttr(default=None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tools = self._build_management_tools()

    def _build_management_tools(self) -> Dict[str, ToolBase]:
        protected_tool_names = {
            "RegisterRuntimeTool",
            "InspectRuntimeTool",
            "ListRuntimeTools",
            "UnregisterRuntimeTool",
            "ReplaceRuntimeTool",
        }
        return {
            "RegisterRuntimeTool": RegisterRuntimeTool(
                toolkit=self,
                protected_tool_names=protected_tool_names,
                factory=self._build_tool,
            ),
            "InspectRuntimeTool": InspectRuntimeTool(toolkit=self),
            "ListRuntimeTools": ListRuntimeTools(toolkit=self),
            "UnregisterRuntimeTool": UnregisterRuntimeTool(
                toolkit=self, protected_tool_names=protected_tool_names
            ),
            "ReplaceRuntimeTool": ReplaceRuntimeTool(
                toolkit=self,
                protected_tool_names=protected_tool_names,
                factory=self._build_tool,
            ),
        }

    def bind_recipe_dispatch(self, dispatch: Callable) -> None:
        """Configure the application dispatcher for recipe steps."""
        self._recipe_dispatch = dispatch

    def _build_tool(self, spec):
        if isinstance(spec, Mapping) and spec.get("type") == "RecipeTool":
            if self._recipe_dispatch is None:
                raise ValueError("Recipe dispatch is not configured")
            return RecipeTool.model_validate(
                {**spec, "dispatch": self._recipe_dispatch}
            )
        return build_tool_from_spec(spec)

    def add_tool(self, tool):
        super().add_tool(tool)
        self.revision += 1

    def remove_tool(self, tool_name):
        super().remove_tool(tool_name)
        self.revision += 1
