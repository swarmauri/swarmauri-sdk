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
    # Create an instance of AccessibilityToolkit
    toolkit = AccessibilityToolkit()

    # Serialize the toolkit to JSON
    serialized_data = toolkit.model_dump_json()

    # Deserialize the JSON back to an AccessibilityToolkit object
    deserialized_toolkit = AccessibilityToolkit.model_validate_json(serialized_data)

    # Assert that the ID and content of the toolkit remain the same after serialization and deserialization
    assert toolkit.id == deserialized_toolkit.id
    assert toolkit.get_tool_names() == deserialized_toolkit.get_tool_names()

    # Optionally, ensure that the entire object is equal, including the state of each tool
    assert toolkit == deserialized_toolkit

@pytest.mark.unit
def test_add_tool():
    toolkit = Toolkit()
    initial_tool_count = len(toolkit.get_tool_names())
    # Replace Tool() with an actual tool class or instance if available
    new_tool = AutomatedReadabilityIndexTool(name='NewTool')
    toolkit.add_tool(new_tool)
    assert len(toolkit.get_tool_names()) == initial_tool_count + 1
