from swarmauri.standard.tools.concrete.CalculatorTool import CalculatorTool


def test_initialization():
    def test():
        tool = CalculatorTool()
        assert type(tool.path) == str
        assert type(tool.id) == str

    test()

def test_call():
    def test():
        tool = CalculatorTool()
        assert tool('add', 2, 3) == str(5)
        assert tool('subtract', 17, 2) == str(15)
        assert tool('multiply', 100, 5) == str(500)
        assert tool('divide', 100, 2) == str(50.0)
    test()