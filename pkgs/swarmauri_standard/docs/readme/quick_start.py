from swarmauri_standard.tools.CalculatorTool import CalculatorTool

calculator = CalculatorTool()
result = calculator("add", 5, 3)

assert result == {"operation": "add", "calculated_result": "8.0"}
