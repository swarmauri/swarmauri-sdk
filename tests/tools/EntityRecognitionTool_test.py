import pytest
import json
from swarmauri.community.tools.concrete.EntityRecognitionTool import EntityRecognitionTool
from swarmauri.standard.tools.concrete.Parameter import Parameter

@pytest.mark.unit
def test_type():
    tool = EntityRecognitionTool(name="EntityRecognitionTool", parameters=[Parameter(name="text", type="string", description="The text for entity recognition", required=True)])
    assert tool.type == 'ToolBase', "Type should be 'ToolBase'"

@pytest.mark.unit
def test_resource():
    tool = EntityRecognitionTool(name="EntityRecognitionTool", parameters=[Parameter(name="text", type="string", description="The text for entity recognition", required=True)])
    assert tool.resource == 'Tool', "Resource should be 'Tool'"

@pytest.mark.unit
def test_serialization():
    tool = EntityRecognitionTool(name="EntityRecognitionTool", parameters=[Parameter(name="text", type="string", description="The text for entity recognition", required=True)])
    
    # Test serialization
    serialized_tool = tool.dict()
    assert 'name' in serialized_tool, "Serialized tool should include 'name'"
    assert 'parameters' in serialized_tool, "Serialized tool should include 'parameters'"
    
    # Test deserialization
    deserialized_tool = EntityRecognitionTool(**serialized_tool)
    assert deserialized_tool.name == tool.name, "Deserialized tool should have the same 'name'"
    assert deserialized_tool.parameters == tool.parameters, "Deserialized tool should have the same 'parameters'"

@pytest.mark.unit
def test_access():
    tool = EntityRecognitionTool(name="EntityRecognitionTool", parameters=[Parameter(name="text", type="string", description="The text for entity recognition", required=True)])
    
    # Test calling the tool
    text = "Barack Obama was born in Hawaii."
    result = tool(text=text)
    
    # Check if the result is a dictionary and not empty
    assert isinstance(result, dict), "Result should be a dictionary"
    assert len(result) > 0, "Result should not be empty"

@pytest.mark.unit
def test_functionality():
    tool = EntityRecognitionTool(name="EntityRecognitionTool", parameters=[Parameter(name="text", type="string", description="The text for entity recognition", required=True)])
    
    # Test functionality of __call__ method
    text = "Apple Inc. is an American multinational technology company."
    result = tool(text=text)
    
    # Check if the result is a JSON string and can be deserialized into a dictionary
    assert isinstance(result, str), "Result should be a JSON string"
    try:
        result_dict = json.loads(result)
        assert isinstance(result_dict, dict), "Deserialized result should be a dictionary"
    except json.JSONDecodeError:
        pytest.fail("Result could not be deserialized into a dictionary")
    
    # Check if 'ORG'(organization) is recognized
    assert 'ORG' in result_dict, "Result should include 'ORG' entity type"
