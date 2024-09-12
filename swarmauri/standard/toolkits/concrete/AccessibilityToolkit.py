from typing import Literal, Any
from pydantic import Field, model_validator
from swarmauri.standard.toolkits.base.ToolkitBase import ToolkitBase
from swarmauri.standard.tools.concrete.AutomatedReadabilityIndexTool import (
    AutomatedReadabilityIndexTool,
)
from swarmauri.standard.tools.concrete.ColemanLiauIndexTool import ColemanLiauIndexTool
from swarmauri.standard.tools.concrete.FleschKincaidTool import FleschKincaidTool
from swarmauri.standard.tools.concrete.FleschReadingEaseTool import (
    FleschReadingEaseTool,
)
from swarmauri.standard.tools.concrete.GunningFogTool import GunningFogTool


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

    @model_validator(mode="wrap")
    @classmethod
    def validate_model(cls, values: Any, handler: Any):
        # Extract the tools and validate their types manually
        tools = values.get("tools", {})

        # Map of tool types to their corresponding classes
        tool_class_map = {
            "AutomatedReadabilityIndexTool": AutomatedReadabilityIndexTool,
            "ColemanLiauIndexTool": ColemanLiauIndexTool,
            "FleschKincaidTool": FleschKincaidTool,
            "FleschReadingEaseTool": FleschReadingEaseTool,
            "GunningFogTool": GunningFogTool,
        }

        for tool_name, tool_data in tools.items():
            if isinstance(tool_data, dict):
                tool_type = tool_data.get("type")
                tool_id = tool_data.get("id")  # Preserve the ID if it exists

                # Map types to the correct tool class and instantiate the tool
                tool_class = tool_class_map.get(tool_type)
                if tool_class:
                    # Create an instance of the tool class
                    tools[tool_name] = tool_class(**tool_data)
                    tools[
                        tool_name
                    ].id = tool_id  # Ensure the tool ID is not changed unintentionally
                else:
                    raise ValueError(f"Unknown tool type: {tool_type}")

        values["tools"] = tools
        return handler(values)
