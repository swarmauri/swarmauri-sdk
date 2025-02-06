from typing import Literal
from pydantic import Field

from swarmauri_base.toolkits.ToolkitBase import ToolkitBase

from swarmauri_standard.tools.AutomatedReadabilityIndexTool import (
<<<<<<< Updated upstream
    AutomatedReadabilityIndexTool,
)
from swarmauri_standard.tools.ColemanLiauIndexTool import ColemanLiauIndexTool
from swarmauri_standard.tools.FleschKincaidTool import FleschKincaidTool
from swarmauri_standard.tools.FleschReadingEaseTool import (
    FleschReadingEaseTool,
)
from swarmauri_standard.tools.GunningFogTool import GunningFogTool
=======
    AutomatedReadabilityIndexTool
)
from swarmauri_standard.tools.ColemanLiauIndexTool import (
    ColemanLiauIndexTool
    )

from swarmauri_standard.tools.FleschKincaidTool import (
    FleschKincaidTool
    )

from swarmauri_standard.tools.FleschReadingEaseTool import (
    GunningFogTool
    )
>>>>>>> Stashed changes

from swarmauri_core.ComponentBase import ComponentBase


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