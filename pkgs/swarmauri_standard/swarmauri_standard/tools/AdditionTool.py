from typing import List, Literal, Dict
from pydantic import Field
from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ToolBase, "AdditionTool")
class AdditionTool(ToolBase):
    version: str = "0.0.1"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="x",
                input_type="integer",
                description="The left operand",
                required=True,
            ),
            Parameter(
                name="y",
                input_type="integer",
                description="The right operand",
                required=True,
            ),
        ]
    )

    name: str = "AdditionTool"
    description: str = "This tool has two numbers together"
    type: Literal["AdditionTool"] = "AdditionTool"

    def __call__(self, x: int, y: int) -> Dict[str, str]:
        """
        Add two numbers x and y and return the sum.

        Parameters:
        - x (int): The first number.
        - y (int): The second number.

        Returns:
        - Dict[str, str]: Containing the function result
        """
        return {"sum": str(x + y)}
