from swarmauri.standard.tools.concrete.CalculatorTool import CalculatorTool


def test_initialization():
    def test():
        tool = CalculatorTool()
        assert tool('add', 2, 3) == str(5)
    test()

def test_call():
    def test():
        tool = CalculatorTool()
        assert tool('add', 2, 3) == str(5)
    test()
    
