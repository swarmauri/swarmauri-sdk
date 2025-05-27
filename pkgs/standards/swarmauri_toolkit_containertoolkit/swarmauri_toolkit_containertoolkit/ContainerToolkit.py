from typing import Dict
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase
from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion

from swarmauri_tool_containernewsession import ContainerNewSessionTool
from swarmauri_tool_containerfeedchars import ContainerFeedCharsTool
from swarmauri_tool_containermakepr import ContainerMakePrTool


@ComponentBase.register_type(ToolkitBase, "ContainerToolkit")
class ContainerToolkit(ToolkitBase):
    tools: Dict[str, SubclassUnion[ToolBase]] = {}

    def __init__(
        self, container_name: str | None = None, image: str | None = None, **kwargs
    ):
        super().__init__(**kwargs)
        self.tools = {
            "ContainerNewSessionTool": ContainerNewSessionTool(
                container_name=container_name,
                image=image,
            ),
            "ContainerFeedCharsTool": ContainerFeedCharsTool(
                container_name=container_name,
            ),
            "ContainerMakePrTool": ContainerMakePrTool(
                container_name=container_name,
            ),
        }
