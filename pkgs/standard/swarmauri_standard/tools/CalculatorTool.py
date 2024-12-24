from swarmauri_core.typing import SubclassUnion
from typing import List, Literal, Dict
from pydantic import Field
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter


class CalculatorTool(ToolBase):
    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="operation",
                type="string",
                description="The arithmetic operation to perform ('add', 'subtract', 'multiply', 'divide').",
                required=True,
                enum=["add", "subtract", "multiply", "divide"],
            ),
            Parameter(
                name="x",
                type="number",
                description="The left operand for the operation.",
                required=True,
            ),
            Parameter(
                name="y",
                type="number",
                description="The right operand for the operation.",
                required=True,
            ),
        ]
    )
    name: str = "CalculatorTool"
    description: str = "Performs basic arithmetic operations."
    type: Literal["CalculatorTool"] = "CalculatorTool"

    def __call__(self, operation: str, x: float, y: float) -> Dict[str, str]:
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
            return {"operation": operation, "calculated_result": str(result)}
        except Exception as e:
            return f"An error occurred: {str(e)}"


SubclassUnion.update(baseclass=ToolBase, type_name="CalculatorTool", obj=CalculatorTool)
