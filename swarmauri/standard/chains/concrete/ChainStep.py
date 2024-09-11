from typing import Literal
from pydantic import BaseModel, field_validator
from swarmauri.standard.chains.base.ChainStepBase import ChainStepBase
from swarmauri.standard.tools.base.ToolBase import ToolBase

# Import your tool classes
from swarmauri.standard.tools.concrete.AdditionTool import AdditionTool
from swarmauri.standard.tools.concrete.AutomatedReadabilityIndexTool import (
    AutomatedReadabilityIndexTool,
)
from swarmauri.standard.tools.concrete.ColemanLiauIndexTool import ColemanLiauIndexTool


class ChainStep(ChainStepBase):
    """
    Represents a single step within an execution chain.
    """

    type: Literal["ChainStep"] = "ChainStep"
    method: ToolBase  # The method must be a ToolBase instance or subclass

    # Custom validator for the method field during deserialization
    @field_validator("method", mode="before")
    def validate_method(cls, value):
        # Perform manual validation and instantiation based on the type
        if isinstance(value, dict) and "type" in value:
            tool_type = value["type"]
            if tool_type == "AdditionTool":
                return AdditionTool(**value)
            elif tool_type == "AutomatedReadabilityIndexTool":
                return AutomatedReadabilityIndexTool(**value)
            elif tool_type == "ColemanLiauIndexTool":
                return ColemanLiauIndexTool(**value)
            # Add other tools as necessary
            else:
                raise ValueError(f"Unsupported tool type: {tool_type}")
        elif isinstance(value, ToolBase):
            return value  # It's already a ToolBase instance
        raise ValueError("Invalid value for method field")

    @classmethod
    def model_validate_json(cls, data: str):
        """Custom deserialization method to handle method field validation."""
        import json

        # Deserialize JSON string to dictionary
        data_dict = json.loads(data)

        # Manually validate and handle tools
        method_data = data_dict.get("method")
        if isinstance(method_data, dict):
            tool_type = method_data.get("type")
            if tool_type == "AdditionTool":
                data_dict["method"] = AdditionTool(**method_data)
            elif tool_type == "AutomatedReadabilityIndexTool":
                data_dict["method"] = AutomatedReadabilityIndexTool(**method_data)
            elif tool_type == "ColemanLiauIndexTool":
                data_dict["method"] = ColemanLiauIndexTool(**method_data)
            # Add more tools if needed
            else:
                raise ValueError(f"Unknown tool type: {tool_type}")

        return super().model_validate(data_dict)
