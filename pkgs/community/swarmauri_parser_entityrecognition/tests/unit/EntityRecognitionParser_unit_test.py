import pytest
from swarmauri_parser_entityrecognition.EntityRecognitionParser import (
    EntityRecognitionParser as Parser,
)


@pytest.fixture(scope="module")
def parser():
    """Fixture to provide a parser instance for tests."""
    return Parser()


@pytest.mark.unit
def test_ubc_resource(parser):
    assert parser.resource == "Parser"


@pytest.mark.unit
def test_ubc_type(parser):
    assert parser.type == "BERTEmbeddingParser"


@pytest.mark.unit
def test_serialization(parser):
    assert parser.id == Parser.model_validate_json(parser.model_dump_json()).id


@pytest.mark.unit
def test_parse(parser):
    try:
        documents = parser.parse("One more large chapula please.")
        assert documents[0].resource == "Document"
        assert documents[0].content == "One more large chapula please."
        assert documents[0].metadata["noun_phrases"] == ["large chapula"]
    except Exception as e:
        pytest.fail(f"Parser failed with error: {str(e)}")
