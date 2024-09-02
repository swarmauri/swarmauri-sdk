import pytest
from swarmauri.standard.tools.concrete.TextLengthTool import TextLengthTool as Tool
from swarmauri.standard.toolkits.concrete.AccessibilityToolkit import AccessibilityToolkit as Toolkit

@pytest.mark.unit
def test_ubc_resource():
    toolkit = Toolkit()
    assert toolkit.resource == 'Toolkit'

@pytest.mark.unit
def test_ubc_type():
    toolkit = Toolkit()
    assert toolkit.type == 'AccessibilityToolkit'

@pytest.mark.unit
def test_serialization():
    toolkit = Toolkit()
    tool_name = 'TextLengthTool'
    tool = Tool(name=tool_name)
    toolkit.add_tool(tool)
    assert toolkit.id == Toolkit.model_validate_json(toolkit.model_dump_json()).id
    assert toolkit.get_tool_by_name(tool_name)('hello there!') == {'num_characters': 11, 'num_words': 3, 'num_sentences': 1}

@pytest.mark.unit
def test_add_tool():
    toolkit = Toolkit()
    tool = Tool()
    toolkit.add_tool(tool)
    assert len(toolkit.get_tools()) == 1

@pytest.mark.unit
def test_call_textlength():
    toolkit = Toolkit()
    tool_name = 'TextLengthTool'
    expected_result = {'num_characters': 11, 'num_words': 3, 'num_sentences': 1}
    assert toolkit.get_tool_by_name(tool_name)('hello there!') == expected_result