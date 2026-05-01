from typing import Dict, Literal

from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase

from .RegisterRuntimeTool import RegisterRuntimeTool
from .InspectRuntimeTool import InspectRuntimeTool
from .ListRuntimeTools import ListRuntimeTools
from .UnregisterRuntimeTool import UnregisterRuntimeTool
from .ReplaceRuntimeTool import ReplaceRuntimeTool


@ComponentBase.register_type(ToolkitBase, "RuntimeToolkit")
class RuntimeToolkit(ToolkitBase):
    type: Literal["RuntimeToolkit"] = "RuntimeToolkit"
    tools: Dict[str, SubclassUnion[ToolBase]] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tools = self._build_management_tools()

    def _build_management_tools(self) -> Dict[str, SubclassUnion[ToolBase]]:
        protected_tool_names = {
            "RegisterRuntimeTool",
            "InspectRuntimeTool",
            "ListRuntimeTools",
            "UnregisterRuntimeTool",
            "ReplaceRuntimeTool",
        }
        return {
            "RegisterRuntimeTool": RegisterRuntimeTool(
                toolkit=self, protected_tool_names=protected_tool_names
            ),
            "InspectRuntimeTool": InspectRuntimeTool(toolkit=self),
            "ListRuntimeTools": ListRuntimeTools(toolkit=self),
            "UnregisterRuntimeTool": UnregisterRuntimeTool(
                toolkit=self, protected_tool_names=protected_tool_names
            ),
            "ReplaceRuntimeTool": ReplaceRuntimeTool(
                toolkit=self, protected_tool_names=protected_tool_names
            ),
        }
