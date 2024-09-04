import json
import pytest
from unittest.mock import patch, MagicMock
from transformers import pipeline
from swarmauri.community.tools.concrete.EntityRecognitionTool import EntityRecognitionTool as Tool


@pytest.mark.unit
def test_type():
    tool = Tool()
    assert isinstance(tool, Tool), "Component is not of the expected type."


@pytest.mark.unit
def test_resource():
    tool = Tool()
    text = "Barack Obama was the 44th president of the United States."
    
    with patch('transformers.pipeline') as mock_pipeline:
        mock_ner = MagicMock()
        mock_ner.return_value = [{"entity": "PER", "word": "Barack Obama"}, {"entity": "ORG", "word": "United States"}]
        mock_pipeline.return_value = mock_ner

        result = tool(text)
        assert isinstance(result, str), "The output is not of the expected type."
        assert "PER" in result and "ORG" in result, "Resource handling failed."


@pytest.mark.unit
def test_serialization():
    tool = Tool()
    entities = {"PER": ["Barack Obama"], "ORG": ["United States"]}

    # Test serialization
    serialized_data = json.dumps(entities)
    assert serialized_data == '{"PER": ["Barack Obama"], "ORG": ["United States"]}', "Serialization failed."

    # Test deserialization
    deserialized_data = json.loads(serialized_data)
    assert deserialized_data == entities, "Deserialization failed."


@pytest.mark.unit
def test_access():
    tool = Tool()
    assert callable(tool), "Component is not callable as expected."


@pytest.mark.unit
def test_functionality():
    tool = Tool()
    text = "Barack Obama was the 44th president of the United States."

    with patch('transformers.pipeline') as mock_pipeline:
        mock_ner = MagicMock()
        mock_ner.return_value = [{"entity": "PER", "word": "Barack Obama"}, {"entity": "ORG", "word": "United States"}]
        mock_pipeline.return_value = mock_ner

        result = tool(text)
        expected_result = '{"PER": ["Barack Obama"], "ORG": ["United States"]}'
        assert result == expected_result, "Functionality test failed."

    with patch('transformers.pipeline', side_effect=Exception("Error")):
        with pytest.raises(Exception, match="Error"):
            tool(text)
