import pytest
from swarmauri.standard.tools.concrete.AutomatedReadabilityIndexTool import AutomatedReadabilityIndexTool
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
    tool_name = 'AutomatedReadabilityIndexTool'
    assert toolkit.id == Toolkit.model_validate_json(toolkit.model_dump_json()).id
    assert toolkit.get_tool_by_name(tool_name)('hello there!') == {'num_characters': 11, 'num_words': 3, 'num_sentences': 1}

@pytest.mark.unit
def test_tool_count():
    toolkit = Toolkit()
    assert len(toolkit.get_tools()) == 5

@pytest.mark.unit
def test_add_tool():
    toolkit = Toolkit()
    tool = AutomatedReadabilityIndexTool(name='ari_tool_2')
    toolkit.add_tool(tool)
    assert len(toolkit.get_tools()) == 6

@pytest.mark.unit
def test_call_automated_readability_index_tool():
    toolkit = Toolkit()
    tool_name = 'AutomatedReadabilityIndexTool'
    expected_result = {'num_characters': 11, 'num_words': 3, 'num_sentences': 1}
    assert toolkit.get_tool_by_name(tool_name)('hello there!') == expected_result