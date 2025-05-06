"""
CalculatorTool.py

This module defines the CalculatorTool, a component that performs basic arithmetic operations.
It leverages the ToolBase and ComponentBase classes from the swarmauri framework to integrate
seamlessly with the system's tool architecture.

The CalculatorTool supports addition, subtraction, multiplication, and division operations,
taking two numerical operands as input and returning the result of the specified operation.
"""

from typing import List, Literal, Dict
from pydantic import Field
from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ToolBase, "CalculatorTool")
class CalculatorTool(ToolBase):
    """
    CalculatorTool is a tool that performs basic arithmetic operations such as addition,
    subtraction, multiplication, and division on two numerical operands.

    Attributes:
        version (str): The version of the CalculatorTool.
        parameters (List[Parameter]): A list of parameters required to perform calculations.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["CalculatorTool"]): The type identifier for the tool.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="operation",
                input_type="string",
                description="The arithmetic operation to perform ('add', 'subtract', 'multiply', 'divide').",
                required=True,
                enum=["add", "subtract", "multiply", "divide"],
            ),
            Parameter(
                name="x",
                input_type="number",
                description="The left operand for the operation.",
                required=True,
            ),
            Parameter(
                name="y",
                input_type="number",
                description="The right operand for the operation.",
                required=True,
            ),
        ]
    )
    name: str = "CalculatorTool"
    description: str = "Performs basic arithmetic operations."
    type: Literal["CalculatorTool"] = "CalculatorTool"

    def __call__(self, operation: str, x: float, y: float) -> Dict[str, str]:
        """
        Executes the specified arithmetic operation on the provided operands.

        Args:
            operation (str): The arithmetic operation to perform. Must be one of
                             'add', 'subtract', 'multiply', or 'divide'.
            x (float): The left operand for the operation.
            y (float): The right operand for the operation.

        Returns:
            Dict[str, str]: A dictionary containing the operation performed and the result
                            as a string. If an error occurs (e.g., division by zero or
                            unknown operation), an error message is returned instead.

        Example:
            >>> calculator = CalculatorTool()
            >>> calculator("add", 5, 3)
            {'operation': 'add', 'calculated_result': '8.0'}
        """
        try:
            if operation == "add":
                result = x + y
            elif operation == "subtract":
                result = x - y
            elif operation == "multiply":
                result = x * y
            elif operation == "divide":
                if y == 0:
                    return {"error": "Error: Division by zero."}
                result = x / y
            else:
                return {"error": "Error: Unknown operation."}
            return {"operation": operation, "calculated_result": str(result)}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}
