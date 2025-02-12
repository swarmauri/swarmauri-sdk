import pytest
from swarmauri_tool_sentimentanalysis.SentimentAnalysisTool import (
    SentimentAnalysisTool as Tool,
)


@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == "SentimentAnalysisTool"


@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) is str


@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.parametrize(
    "text, expected_labels",
    [
        ("I love this product!", ["POSITIVE", "NEGATIVE", "NEUTRAL"]),
        ("I hate this product!", ["NEGATIVE", "POSITIVE", "NEUTRAL"]),
        ("This product is okay.", ["NEUTRAL", "POSITIVE", "NEGATIVE"]),
    ],
)
@pytest.mark.unit
def test_call(text, expected_labels):
    tool = Tool()
    result = tool(text)

    assert result["sentiment"] in expected_labels

    assert isinstance(result, dict)
    assert "sentiment" in result

    assert not hasattr(tool, "analyzer")
