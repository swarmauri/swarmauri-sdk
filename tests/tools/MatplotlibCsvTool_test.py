import pytest
from swarmauri.standard.tools.concrete.MatplotlibCsvTool import MatplotlibCsvTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'


@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'MatplotlibCsvTool'


@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) == str

@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id

@pytest.mark.unit
def test_call():
    tool = Tool()
    input_text = "dummy text"
    assert tool(input_text) == "dummy text"