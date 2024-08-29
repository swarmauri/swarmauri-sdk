import pytest
from swarmauri.standard.tools.concrete.WeatherTool import WeatherTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_call():
    tool = Tool()
    location = 'Dallas'
    assert tool(location) == "Weather Info: ('Dallas', 'fahrenheit')\n"
