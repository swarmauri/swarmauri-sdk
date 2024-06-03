from swarmauri.standard.tools.concrete.TestTool import TestTool as tTool

def test_initialization():
    def test():
        test_tool = tTool()
    test()

def test_call():
    def test():
        test_tool = tTool()
        success_message = 'Program Opened: calc'
        assert test_tool('calc') == success_message
    test()
