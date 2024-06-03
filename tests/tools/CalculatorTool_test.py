from swarmauri.standard.tools.concrete.CalculatorTool import CalculatorTool

def initialize_test():
    tool = CalculatorTool()
    assert tool('add', 2, 3) == str(5)


def assert_call():
    tool = CalculatorTool()
    assert tool('add', 2, 3) == str(5)
    
initialize_test()
assert_call()
