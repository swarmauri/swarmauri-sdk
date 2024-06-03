from swarmauri.standard.tools.concrete.CalculatorTool import CalculatorTool

def initialize_test():
    tool = CalculatorTool()
    assert str(5) == tool('add', 2, 3)
initialize_test()
