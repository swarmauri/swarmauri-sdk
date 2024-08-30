import pytest
from swarmauri.standard.tools.concrete.CalculatorTool import CalculatorTool

@pytest.mark.unit
def test_ubc_resource():
    tool = CalculatorTool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'CalculatorTool'

@pytest.mark.unit
def test_initialization():
    tool = CalculatorTool()
    assert type(tool.swm_path) == str
    assert type(tool.id) == str


@pytest.mark.unit
def test_call():
    tool = CalculatorTool()
    assert tool('add', 2, 3) == str(5)
    assert tool('subtract', 17, 2) == str(15)
    assert tool('multiply', 100, 5) == str(500)
    assert tool('divide', 100, 2) == str(50.0)