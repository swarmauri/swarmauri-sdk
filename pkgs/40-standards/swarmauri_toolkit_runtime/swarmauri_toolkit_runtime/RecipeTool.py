from collections.abc import Callable
from typing import Any, Literal

from pydantic import BaseModel, Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase


class RecipeStep(BaseModel):
    """Call one installed tool with literals or input references."""

    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)


@ComponentBase.register_type(ToolBase, "RecipeTool")
class RecipeTool(ToolBase):
    """Run a sequence of existing tool calls through a host dispatcher."""

    type: Literal["RecipeTool"] = "RecipeTool"
    steps: list[RecipeStep] = Field(min_length=1, max_length=32)
    dispatch: Callable[[str, dict[str, Any]], dict[str, Any]] = Field(
        exclude=True
    )

    def __call__(self, **inputs):
        declared = {parameter.name for parameter in self.parameters}
        required = {
            parameter.name
            for parameter in self.parameters
            if parameter.required
        }
        if inputs.keys() - declared or required - inputs.keys():
            raise ValueError("Recipe inputs do not match its parameters")
        results = []
        for step in self.steps:
            arguments = {
                key: inputs[value["input"]]
                if isinstance(value, dict) and value.keys() == {"input"}
                else value
                for key, value in step.arguments.items()
            }
            result = self.dispatch(step.tool, arguments)
            results.append(result)
            if result.get("status") != "completed":
                break
        return {"steps": results}
