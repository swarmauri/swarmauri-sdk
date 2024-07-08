from typing import List, Literal
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase 
from swarmauri.standard.tools.concrete.Parameter import Parameter

class CalculatorTool(ToolBase):
    version: str = "1.0.0"
    parameters: List[Parameter] = Field(default_factory=lambda: [
        Parameter(
            name="operation",
            type="string",
            description="The arithmetic operation to perform ('add', 'subtract', 'multiply', 'divide').",
            required=True,
            enum=["add", "subtract", "multiply", "divide"]
        ),
        Parameter(
            name="x",
            type="number",
            description="The left operand for the operation.",
            required=True
        ),
        Parameter(
            name="y",
            type="number",
            description="The right operand for the operation.",
            required=True
        )
    ])
    name: str = 'CalculatorTool'
    description: str = "Performs basic arithmetic operations."
    type: Literal['CalculatorTool'] = 'CalculatorTool'

    def __call__(self, operation: str, x: float, y: float) -> str:
        try:
            if operation == "add":
                result = x + y
            elif operation == "subtract":
                result = x - y
            elif operation == "multiply":
                result = x * y
            elif operation == "divide":
                if y == 0:
                    return "Error: Division by zero."
                result = x / y
            else:
                return "Error: Unknown operation."
            return str(result)
        except Exception as e:
            return f"An error occurred: {str(e)}"
