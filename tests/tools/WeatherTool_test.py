import pytest
from swarmauri.standard.tools.concrete.WeatherTool import WeatherTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    def test():
        tool = Tool()
        assert tool.resource == 'Tool'
    test()

@pytest.mark.unit
def test_call():
    def test():
        location = 'Dallas'
        tool = Tool(location)
        print(tool())
        assert tool() == 'Weather Info: ("Dallas", "fahrenheit")'
    test()
