import pytest
from swarmauri.standard.tools.concrete.SentenceComplexityTool import SentenceComplexityTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'SentenceComplexityTool'

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
    valid_text = "This is a simple sentence. This is another sentence, with a clause."

    expected_results = {
        "average_sentence_length": pytest.approx(7.5, rel=1e-2),
        "average_clauses_per_sentence": pytest.approx(1.5, rel=1e-2)
    }

    result = tool(valid_text)

    assert result["average_sentence_length"] == expected_results["average_sentence_length"]
    assert result["average_clauses_per_sentence"] == expected_results["average_clauses_per_sentence"]