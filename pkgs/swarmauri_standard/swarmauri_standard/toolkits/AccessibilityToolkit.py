from typing import Dict, Literal

from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase
from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion

from swarmauri_standard.tools.AutomatedReadabilityIndexTool import (
    AutomatedReadabilityIndexTool,
)
from swarmauri_standard.tools.ColemanLiauIndexTool import ColemanLiauIndexTool

from swarmauri_standard.tools.FleschKincaidTool import FleschKincaidTool

from swarmauri_standard.tools.FleschReadingEaseTool import FleschReadingEaseTool

from swarmauri_standard.tools.GunningFogTool import GunningFogTool


@ComponentBase.register_type(ToolkitBase, "AccessibilityToolkit")
class AccessibilityToolkit(ToolkitBase):
    type: Literal["AccessibilityToolkit"] = "AccessibilityToolkit"
    tools: Dict[str, SubclassUnion[ToolBase]] = {
        "AutomatedReadabilityIndexTool": AutomatedReadabilityIndexTool(),
        "ColemanLiauIndexTool": ColemanLiauIndexTool(),
        "FleschKincaidTool": FleschKincaidTool(),
        "FleschReadingEaseTool": FleschReadingEaseTool(),
        "GunningFogTool": GunningFogTool(),
    }
