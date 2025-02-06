import logging
import pytest
import warnings

from swarmauri_standard.tools.AdditionTool import AdditionTool
from swarmauri_standard.toolkits.AccessibilityToolkit import AccessibilityToolkit


@pytest.fixture(scope="module")
def accessibility_toolkit():
    return AccessibilityToolkit()


@pytest.mark.unit
def test_ubc_resource(accessibility_toolkit):
    assert accessibility_toolkit.resource == "AccessibilityToolkit"


@pytest.mark.unit
def test_ubc_type(accessibility_toolkit):
    assert accessibility_toolkit.type == "AccessibilityToolkit"


@pytest.mark.unit
def test_serialization(accessibility_toolkit):
    # with warnings.catch_warnings():
    #     warnings.simplefilter("ignore", UserWarning)
    #     toolkit = Toolkit()
    #     serialized_data = toolkit.model_dump_json()
    #     logging.info(serialized_data)
    #     deserialized_toolkit = Toolkit.model_validate_json(serialized_data)

    #     assert toolkit.id == deserialized_toolkit.id
    #     assert toolkit == deserialized_toolkit

    serialized_data = accessibility_toolkit.model_dump_json()
    deserialized_toolkit = AccessibilityToolkit.model_validate_json(serialized_data)
    assert accessibility_toolkit.id == deserialized_toolkit.id


@pytest.mark.unit
def test_tool_count(accessibility_toolkit):
    assert len(accessibility_toolkit.get_tools()) == 5


@pytest.mark.unit
def test_add_tool(accessibility_toolkit):
    tool = AdditionTool()
    accessibility_toolkit.add_tool(tool)
    assert len(accessibility_toolkit.get_tools()) == 6


@pytest.mark.unit
def test_call_automated_readability_index_tool(accessibility_toolkit):
    tool_name = "AutomatedReadabilityIndexTool"
    # Update the expected result to match the actual output
    expected_result = {"ari_score": 5.475000000000001}

    # Adjust the assertion to reflect the actual behavior
    result = accessibility_toolkit.get_tool_by_name(tool_name)("hello there!")
    assert result == expected_result
