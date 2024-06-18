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
        tool = Tool()
        location = 'Dallas'
        assert tool(location) == 'Weather Info: ("Dallas", "fahrenheit")'
    test()
