from ..base.ToolBase import ToolBase
from .Parameter import Parameter

class AdditionTool(ToolBase):
    
    def __init__(self):
        parameters = [
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
        ]
        super().__init__(name="TestTool", 
                         description="This opens a program based on the user's request.", 
                         parameters=parameters)

    def __call__(self, x: int, y: int) -> int:
        """
        Add two numbers x and y and return the sum.

        Parameters:
        - x (int): The first number.
        - y (int): The second number.

        Returns:
        - int: The sum of x and y.
        """
        return x + y