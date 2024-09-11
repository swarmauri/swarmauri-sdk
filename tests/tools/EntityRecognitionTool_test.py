from unittest.mock import MagicMock, patch

import pytest
from swarmauri.community.tools.concrete.EntityRecognitionTool import EntityRecognitionTool as Tool

@pytest.mark.unit
def test_type():
    tool = Tool()
    assert tool.type == 'EntityRecognitionTool', "Type should be 'ToolBase'"

@pytest.mark.unit
def test_resource():
    tool = Tool()
    assert tool.resource == 'Tool', "Resource should be 'Tool'"

@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id

def test_call():
    sample_text = "John Doe works at OpenAI."
    mock_entities = [
        {"entity": "PER", "word": "John Doe"},
        {"entity": "ORG", "word": "OpenAI"}
    ]
    expected_output = '{"PER": ["John Doe"], "ORG": ["OpenAI"]}'

    tool = Tool()

    with patch('transformers.pipeline') as mock_pipeline:
        mock_pipeline.return_value = MagicMock(return_value=mock_entities)

        result = tool(sample_text)

        assert result == expected_output

        mock_pipeline.assert_called_once_with("ner")

