from typing import Dict
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase
from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion

from swarmauri_tool_containernewsession import ContainerNewSessionTool
from swarmauri_tool_containerfeedchars import ContainerFeedCharsTool
from swarmauri_tool_containermakepr import ContainerMakePrTool


@ComponentBase.register_type(ToolkitBase, "ContainerToolkit")
class ContainerToolkit(ToolkitBase):
    tools: Dict[str, SubclassUnion[ToolBase]] = {
        "ContainerNewSessionTool": ContainerNewSessionTool(),
        "ContainerFeedCharsTool": ContainerFeedCharsTool(),
        "ContainerMakePrTool": ContainerMakePrTool(),
    }
