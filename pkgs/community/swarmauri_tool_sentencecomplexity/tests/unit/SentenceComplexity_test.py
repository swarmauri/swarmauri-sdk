import pytest
from swarmauri_tool_sentencecomplexity import (
    SentenceComplexityTool as Tool,
)


@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == "SentenceComplexityTool"


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

    expected_keys = {"average_sentence_length", "average_clauses_per_sentence"}

    expected_results = {
        "average_sentence_length": pytest.approx(7.5, rel=1e-2),
        "average_clauses_per_sentence": pytest.approx(1.5, rel=1e-2),
    }

    result = tool(valid_text)

    assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"
    assert expected_keys.issubset(
        result.keys()
    ), f"Expected keys {expected_keys} but got {result.keys()}"

    assert isinstance(
        result.get("average_sentence_length"), float
    ), f"Expected float, but got {type(result.get('average_sentence_length')).__name__}"
    assert isinstance(
        result.get("average_clauses_per_sentence"), float
    ), f"Expected float, but got {type(result.get('average_clauses_per_sentence')).__name__}"

    assert (
        result.get("average_sentence_length")
        == expected_results["average_sentence_length"]
    ), f"Expected Sentence Length is {expected_results['average_sentence_length']}, but got {result.get('average_sentence_length')}"
    assert (
        result.get("average_clauses_per_sentence")
        == result["average_clauses_per_sentence"]
    ), f"Expected Clauses per Sentence is {result['average_clauses_per_sentence']}, but got {result.get('average_clauses_per_sentence')}"
