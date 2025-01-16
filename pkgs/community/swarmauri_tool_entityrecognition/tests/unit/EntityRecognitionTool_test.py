import json
import pytest
from swarmauri_tool_entityrecognition.EntityRecognitionTool import (
    EntityRecognitionTool as Tool,
)


@pytest.mark.unit
def test_type():
    tool = Tool()
    assert tool.type == "EntityRecognitionTool", "Type should be 'ToolBase'"


@pytest.mark.unit
def test_resource():
    tool = Tool()
    assert tool.resource == "Tool", "Resource should be 'Tool'"


@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.unit
def test_call():
    tool = Tool()

    text = "Apple Inc. is an American multinational technology company."
    expected_result = {"I-ORG": ["Apple", "Inc"], "I-MISC": ["American"]}

    expected_keys = {"entities"}

    result = tool(text=text)

    assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"
    assert expected_keys.issubset(
        result.keys()
    ), f"Expected keys {expected_keys} but got {result.keys()}"
    assert isinstance(
        result.get("entities"), str
    ), f"Expected str, but got {type(result.get('program')).__name__}"

    assert result.get("entities") == json.dumps(
        expected_result
    ), f"Expected Entities result {json.dumps(expected_result)}, but got {result.get('entities')}"
