from swarmauri.standard.tools.base.ToolBase import ToolBase  # Adjust the import path as necessary
from swarmauri.standard.tools.concrete.Parameter import Parameter

class CalculatorTool(ToolBase):
    def __init__(self):
        parameters = [
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
        ]
        super().__init__(name="CalculatorTool", 
                         description="Performs basic arithmetic operations.",
                         parameters=parameters)

    def __call__(self, operation: str, x: float, y: float) -> str:
        """
        Executes the specified arithmetic operation on the given operands.
        
        Parameters:
            operation (str): The arithmetic operation to perform.
            x (float): The left operand.
            y (float): The right operand.
        
        Returns:
            str: Result of the arithmetic operation.
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
                    return "Error: Division by zero."
                result = x / y
            else:
                return "Error: Unknown operation."
            return str(result)
        except Exception as e:
            return f"An error occurred: {str(e)}"