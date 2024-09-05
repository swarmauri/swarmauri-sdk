from typing import Literal, Any
from pydantic import model_validator
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_tool(
            AutomatedReadabilityIndexTool(name="AutomatedReadabilityIndexTool")
        )
        self.add_tool(ColemanLiauIndexTool(name="ColemanLiauIndexTool"))
        self.add_tool(FleschKincaidTool(name="FleschKincaidTool"))
        self.add_tool(FleschReadingEaseTool(name="FleschReadingEaseTool"))
        self.add_tool(GunningFogTool(name="GunningFogTool"))

    @model_validator(mode="wrap")
    def validate_model(cls, values: Any, handler: Any):
        # Extract the tools and validate their types manually
        tools = values.get("tools", {})
        for tool_name, tool_data in tools.items():
            if isinstance(tool_data, dict):
                if tool_data.get("type") == "AutomatedReadabilityIndexTool":
                    tools[tool_name] = AutomatedReadabilityIndexTool(**tool_data)
                elif tool_data.get("type") == "ColemanLiauIndexTool":
                    tools[tool_name] = ColemanLiauIndexTool(**tool_data)
                elif tool_data.get("type") == "FleschKincaidTool":
                    tools[tool_name] = FleschKincaidTool(**tool_data)
                elif tool_data.get("type") == "FleschReadingEaseTool":
                    tools[tool_name] = FleschReadingEaseTool(**tool_data)
                elif tool_data.get("type") == "GunningFogTool":
                    tools[tool_name] = GunningFogTool(**tool_data)

        values["tools"] = tools
        return handler(values)
