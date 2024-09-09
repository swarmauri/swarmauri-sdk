from typing import List, Literal, Dict
import json
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter


class AdditionTool(ToolBase):
    version: str = "0.0.1"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="x", type="integer", description="The left operand", required=True
            ),
            Parameter(
                name="y", type="integer", description="The right operand", required=True
            ),
        ]
    )

    name: str = "AdditionTool"
    description: str = "This tool has two numbers together"
    type: Literal["AdditionTool"] = "AdditionTool"

    def __call__(self, x: float, y: float) -> Dict[str, str]:
        """
        Add two numbers x and y and return the sum.

        Parameters:
        - x (float): The first number.
        - y (float): The second number.

        Returns:
        - Dict[str, str]: Containing the function result
        """
        return {"sum": str(x + y)}
