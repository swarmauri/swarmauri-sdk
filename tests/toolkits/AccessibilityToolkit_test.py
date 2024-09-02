import pytest
from swarmauri.standard.tools.concrete.AutomatedReadabilityIndexTool import AutomatedReadabilityIndexTool
from swarmauri.standard.tools.concrete.ColemanLiauIndexTool import ColemanLiauIndexTool
from swarmauri.standard.tools.concrete.FleschKincaidTool import FleschKincaidTool
from swarmauri.standard.tools.concrete.FleschReadingEaseTool import FleschReadingEaseTool
from swarmauri.standard.tools.concrete.GunningFogTool import GunningFogTool
from swarmauri.standard.toolkits.base.ToolkitBase import ToolkitBase
from swarmauri.standard.toolkits.concrete.AccessibilityToolkit import AccessibilityToolkit as Toolkit

@pytest.mark.unit
def test_ubc_resource():
    toolkit = Toolkit()
    assert toolkit.resource == 'AccessibilityToolkit'

@pytest.mark.unit
def test_ubc_type():
    toolkit = Toolkit()
    assert toolkit.type == 'AccessibilityToolkit'

@pytest.mark.unit
def test_serialization():
    toolkit = Toolkit()
    serialized_data = toolkit.model_dump_json()
    deserialized_toolkit = Toolkit.model_validate_json(serialized_data)

    assert toolkit.id == deserialized_toolkit.id
    assert toolkit.get_tool_names() == deserialized_toolkit.get_tool_names()

    # Optionally, ensure that the entire object is equal, including the state of each tool
    assert toolkit == deserialized_toolkit

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
