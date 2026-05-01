from typing import Dict, Literal

from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase

from .AddToolToToolkitTool import AddToolToToolkitTool
from .GetToolFromToolkitTool import GetToolFromToolkitTool
from .ListToolkitToolsTool import ListToolkitToolsTool
from .RemoveToolFromToolkitTool import RemoveToolFromToolkitTool
from .UpdateToolInToolkitTool import UpdateToolInToolkitTool


@ComponentBase.register_type(ToolkitBase, "ToolCrudToolkit")
class ToolCrudToolkit(ToolkitBase):
    type: Literal["ToolCrudToolkit"] = "ToolCrudToolkit"
    tools: Dict[str, SubclassUnion[ToolBase]] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tools = self._build_management_tools()

    def _build_management_tools(self) -> Dict[str, SubclassUnion[ToolBase]]:
        protected_tool_names = {
            "AddToolToToolkitTool",
            "GetToolFromToolkitTool",
            "ListToolkitToolsTool",
            "RemoveToolFromToolkitTool",
            "UpdateToolInToolkitTool",
        }
        return {
            "AddToolToToolkitTool": AddToolToToolkitTool(
                toolkit=self, protected_tool_names=protected_tool_names
            ),
            "GetToolFromToolkitTool": GetToolFromToolkitTool(toolkit=self),
            "ListToolkitToolsTool": ListToolkitToolsTool(toolkit=self),
            "RemoveToolFromToolkitTool": RemoveToolFromToolkitTool(
                toolkit=self, protected_tool_names=protected_tool_names
            ),
            "UpdateToolInToolkitTool": UpdateToolInToolkitTool(
                toolkit=self, protected_tool_names=protected_tool_names
            ),
        }
