import warnings
import logging
from typing import Literal, Any
from pydantic import Field, model_validator

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from swarmauri.toolkits.base.ToolkitBase import ToolkitBase
from swarmauri_core.typing import SubclassUnion
from swarmauri.tools.base.ToolBase import ToolBase


from swarmauri.tools.concrete.AutomatedReadabilityIndexTool import (
    AutomatedReadabilityIndexTool,
)
from swarmauri.tools.concrete.ColemanLiauIndexTool import ColemanLiauIndexTool
from swarmauri.tools.concrete.FleschKincaidTool import FleschKincaidTool
from swarmauri.tools.concrete.FleschReadingEaseTool import (
    FleschReadingEaseTool,
)
from swarmauri.tools.concrete.GunningFogTool import GunningFogTool


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

        for tool_name, tool_data in tools.items():
            if isinstance(tool_data, dict):
                tool_type = tool_data.get("type")
                tool_id = tool_data.get("id")  # Preserve the ID if it exists

                try:
                    # Assuming SubclassUnion returns a dictionary or a list of tool classes
                    tool_class = next(
                        sc
                        for sc in SubclassUnion.__swm__get_subclasses__(ToolBase)
                        if sc.__name__ == tool_type
                    )

                    logging.info(tool_class)

                    # Create an instance of the tool class
                    tools[tool_name] = tool_class(**tool_data)
                    tools[
                        tool_name
                    ].id = tool_id  # Ensure the tool ID is not changed unintentionally
                except StopIteration:
                    raise ValueError(f"Unknown tool type: {tool_type}")

        values["tools"] = tools
        return handler(values)
