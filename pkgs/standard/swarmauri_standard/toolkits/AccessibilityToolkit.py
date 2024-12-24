from typing import Literal
from pydantic import Field

from swarmauri_base.toolkits.ToolkitBase import ToolkitBase

from swarmauri.tools.concrete import (
    AutomatedReadabilityIndexTool,
    ColemanLiauIndexTool,
    FleschKincaidTool,
    FleschReadingEaseTool,
    GunningFogTool,
)


class AccessibilityToolkit(ToolkitBase):
    type: Literal["AccessibilityToolkit"] = "AccessibilityToolkit"

    resource: str = "AccessibilityToolkit"

    # Explicitly define the tools as fields
    automated_readability_index_tool: AutomatedReadabilityIndexTool = Field(
        default_factory=lambda: AutomatedReadabilityIndexTool(
            name="AutomatedReadabilityIndexTool"
        )
    )
    coleman_liau_index_tool: ColemanLiauIndexTool = Field(
        default_factory=lambda: ColemanLiauIndexTool(name="ColemanLiauIndexTool")
    )
    flesch_kincaid_tool: FleschKincaidTool = Field(
        default_factory=lambda: FleschKincaidTool(name="FleschKincaidTool")
    )
    flesch_reading_ease_tool: FleschReadingEaseTool = Field(
        default_factory=lambda: FleschReadingEaseTool(name="FleschReadingEaseTool")
    )
    gunning_fog_tool: GunningFogTool = Field(
        default_factory=lambda: GunningFogTool(name="GunningFogTool")
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Add all tools to the toolkit using add_tools method
        self.add_tool(self.automated_readability_index_tool)
        self.add_tool(self.coleman_liau_index_tool)
        self.add_tool(self.flesch_kincaid_tool)
        self.add_tool(self.flesch_reading_ease_tool)
        self.add_tool(self.gunning_fog_tool)
