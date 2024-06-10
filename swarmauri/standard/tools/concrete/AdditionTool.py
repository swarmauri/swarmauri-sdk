from typing import List
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase 
from swarmauri.standard.tools.concrete.Parameter import Parameter

class AdditionTool(ToolBase):
    version: str = "0.0.1"
    parameters: List[Parameter] = Field(default_factory=lambda: [
            Parameter(
                name="x",
                type="integer",
                description="The left operand",
                required=True
            ),
            Parameter(
                name="y",
                type="integer",
                description="The right operand",
                required=True
            )
        ])

    description: str = "This tool has two numbers together"


    def __call__(self, x: int, y: int) -> int:
        """
        Add two numbers x and y and return the sum.

        Parameters:
        - x (int): The first number.
        - y (int): The second number.

        Returns:
        - str: The sum of x and y.
        """
        return str(x + y)